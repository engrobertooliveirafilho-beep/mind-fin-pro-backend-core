import json
import unittest
from pathlib import Path
from tests.test_et665_m8_gateway_e2e import M8GatewayE2E
from mind_trader.app.backtest.p2405_paper_gateway import replay_financially_verified_candidate
from mind_trader.app.backtest.p2405_paper_settlement import settle_historical_paper_exit
from mind_trader.app.execution.paper_session import PaperTradingSessionManager


class M9SettlementTests(unittest.TestCase):
    def setUp(self):
        M8GatewayE2E.setUp(self)
        self.accepted = replay_financially_verified_candidate(
            self.candidate,self.gateway,quantity=2,quote_to_account_rate=1,contract_multiplier=1,risk_amount=10,stop_distance=1,
            reward_multiple=2.5,regime_report=self.regime,genome=self.genome,
            authorize_offline_replay=True)
        self.assertEqual(self.accepted["decision"],"ACCEPT_SIMULATED_ORDER",self.accepted)
        self.restarted=PaperTradingSessionManager(str(self.session),str(self.day),str(self.config))
        self.evidence=self.root/"settlement.json"

    def settle(self, **overrides):
        kwargs=dict(broker_ledger_path=str(self.broker),
                    reservation_id=self.accepted["reservation_id"],
                    entry_ts=self.candidate["fill_ts"],
                    exit_ts="2026-01-02T00:00:00",exit_close=110.0,
                    quantity=2.0,quote_to_account_rate=1.0,
                    settlement_evidence_path=self.evidence,
                    authorize_offline_replay=True)
        kwargs.update(overrides)
        return settle_historical_paper_exit(self.restarted,**kwargs)

    def test_net_pnl_restart_and_exactly_once(self):
        result=self.settle()
        self.assertEqual(result["decision"],"M9_HISTORICAL_PAPER_SETTLED",result)
        self.assertAlmostEqual(result["net_account"],result["gross_quote"]-2.0)
        self.assertEqual(self.restarted.reconcile_paper_fills(str(self.broker))["decision"],"PAPER_RECONCILIATION_CLEAN")
        state=json.loads(self.session.read_text())
        self.assertEqual(state["trades"],1)
        self.assertAlmostEqual(state["daily_pnl"],result["net_account"])
        duplicate=self.settle()
        self.assertEqual(duplicate["reason"],"SETTLEMENT_EVIDENCE_ALREADY_EXISTS")
        self.assertEqual(json.loads(self.session.read_text())["trades"],1)
        self.assertEqual(json.loads(self.evidence.read_text())["net_account"],result["net_account"])

    def test_invalid_chronology_blocks_before_recovery(self):
        result=self.settle(exit_ts=self.candidate["fill_ts"])
        self.assertEqual(result["reason"],"INVALID_CHRONOLOGY_OR_RESERVATION")
        self.assertFalse(self.evidence.exists())

    def test_invalid_conversion_blocks(self):
        result=self.settle(quote_to_account_rate=0)
        self.assertEqual(result["reason"],"INVALID_PRICE_SIZE_OR_CONVERSION")
        self.assertEqual(json.loads(self.session.read_text())["trades"],0)

    def test_duplicate_broker_fill_blocks(self):
        row=self.broker.read_text()
        with self.broker.open("a") as f:
            f.write(row)
        result=self.settle()
        self.assertEqual(result["reason"],"BROKER_FILL_NOT_UNIQUE")
        self.assertEqual(json.loads(self.session.read_text())["trades"],0)


if __name__ == "__main__":
    unittest.main()
