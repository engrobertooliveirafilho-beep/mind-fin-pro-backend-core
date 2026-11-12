"""ET665 Fase B: behavioral PAPER gateway/ledger checks. Offline only."""
import json
import unittest
from pathlib import Path
from tests.test_et665_m8_gateway_e2e import M8GatewayE2E
from mind_trader.app.execution.gateway import ExecutionGateway
from mind_trader.app.execution.paper_session import PaperTradingSessionManager


class PaperGatewayBehavioralAudit(unittest.TestCase):
    def setUp(self):
        M8GatewayE2E.setUp(self)

    def submit(self, gateway=None):
        from mind_trader.app.backtest.p2405_paper_gateway import replay_financially_verified_candidate
        return replay_financially_verified_candidate(self.candidate,gateway or self.gateway,
            quantity=1,quote_to_account_rate=1,contract_multiplier=1,
            risk_amount=10,stop_distance=1,reward_multiple=2.5,
            regime_report=self.regime,genome=self.genome,
            authorize_offline_replay=True)

    def fresh_gateway(self):
        return ExecutionGateway(ledger_path=str(self.execution),
            ftmo_config_path=str(self.config),paper_session_path=str(self.session),
            paper_day_ledger_path=str(self.day),paper_broker_ledger_path=str(self.broker))

    def read_rows(self,path):
        return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]

    def test_all_live_modes_blocked_without_broker_ledger(self):
        trade={"symbol":"EURUSD","strategy_id":"SMA_CROSS",
               "client_order_id":"LIVE-DENY","entry":100,"stop":99,
               "target":103,"risk_amount":10,"side":"BUY"}
        for mode in ("LIVE","PRODUCTION","REAL_MONEY","FTMO_REAL","BROKER","INVALID_MODE"):
            with self.subTest(mode=mode):
                result=self.gateway.submit_order(mode,trade,self.regime,self.genome)
                self.assertNotEqual(result["decision"],"ACCEPT_SIMULATED_ORDER")
                self.assertEqual(result["production"],"BLOCKED")
                self.assertFalse(self.broker.exists())

    def test_gateway_restart_blocks_pending_then_settlement_reconciles(self):
        accepted=self.submit()
        self.assertEqual(accepted["decision"],"ACCEPT_SIMULATED_ORDER",accepted)
        broker_rows=self.read_rows(self.broker)
        execution_rows=self.read_rows(self.execution)
        self.assertEqual(len([x for x in broker_rows if x["decision"]=="PAPER_ORDER_ACCEPTED"]),1)
        self.assertEqual(len([x for x in execution_rows if x["decision"]=="ACCEPT_SIMULATED_ORDER"]),1)
        self.assertEqual(execution_rows[-1]["paper_reservation_id"],broker_rows[-1]["order"]["reservation_id"])
        self.assertEqual(accepted["reservation_id"],broker_rows[-1]["order"]["reservation_id"])
        restarted=self.fresh_gateway()
        self.assertEqual(restarted.paper.reconcile_paper_fills(str(self.broker))["decision"],
                         "BLOCK_UNSETTLED_BROKER_FILL")
        retry=self.submit(restarted)
        self.assertNotEqual(retry["decision"],"ACCEPT_SIMULATED_ORDER")
        self.assertEqual(len(self.read_rows(self.broker)),1)
        recovery=restarted.paper.recover_interrupted_paper_fills(str(self.broker))
        self.assertEqual(recovery["decision"],"PAPER_FILLS_ACKNOWLEDGED")
        self.assertEqual(restarted.paper.settle_paper_order(accepted["reservation_id"],-3)["decision"],
                         "PAPER_RESERVATION_SETTLED")
        self.assertEqual(restarted.paper.reconcile_paper_fills(str(self.broker))["decision"],
                         "PAPER_RECONCILIATION_CLEAN")
        self.assertNotEqual(restarted.paper.settle_paper_order(accepted["reservation_id"],-3)["decision"],
                            "PAPER_RESERVATION_SETTLED")
        session=json.loads(self.session.read_text())
        self.assertEqual(session["trades"],1)
        self.assertEqual(session["daily_pnl"],-3)
        settlements=[r for r in self.read_rows(self.day) if r.get("type")=="PAPER_RESERVATION_SETTLED"]
        self.assertEqual(len(settlements),1)
        self.assertEqual(settlements[0]["reservation_id"],accepted["reservation_id"])

    def test_config_drift_blocks_new_orders_without_new_broker_fill(self):
        accepted=self.submit()
        self.assertEqual(accepted["decision"],"ACCEPT_SIMULATED_ORDER",accepted)
        restarted=self.fresh_gateway()
        restarted.paper.recover_interrupted_paper_fills(str(self.broker))
        restarted.paper.settle_paper_order(accepted["reservation_id"],-3)
        cfg=json.loads(self.config.read_text())
        cfg["spread"]=float(cfg["spread"])+0.1
        self.config.write_text(json.dumps(cfg))
        drifted=self.fresh_gateway()
        denied=self.submit(drifted)
        self.assertNotEqual(denied["decision"],"ACCEPT_SIMULATED_ORDER")
        self.assertEqual(len(self.read_rows(self.broker)),1)

    def test_duplicate_client_order_id_rejected_after_restart(self):
        accepted=self.submit()
        self.assertEqual(accepted["decision"],"ACCEPT_SIMULATED_ORDER",accepted)
        restarted=self.fresh_gateway()
        restarted.paper.recover_interrupted_paper_fills(str(self.broker))
        restarted.paper.settle_paper_order(accepted["reservation_id"],-3)
        duplicate=self.submit(restarted)
        self.assertNotEqual(duplicate["decision"],"ACCEPT_SIMULATED_ORDER")
        self.assertEqual(len(self.read_rows(self.broker)),1)


if __name__=="__main__":
    unittest.main()
