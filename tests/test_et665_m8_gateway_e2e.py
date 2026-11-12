import csv
import json
import tempfile
import unittest
from pathlib import Path

from mind_trader.app.backtest.market_core import ingest_ohlcv_csv
from mind_trader.app.backtest.p2405_paper_bridge import prepare_paper_candidates
from mind_trader.app.backtest.p2405_paper_gateway import replay_candidate_to_paper
from mind_trader.app.execution.gateway import ExecutionGateway
from mind_trader.app.execution.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config


class M8GatewayE2E(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        cfg = default_ftmo_config()
        cfg.update(spread=0.2, slippage=0.1, commission=0.5)
        self.config = self.root / "ftmo.json"
        self.config.write_text(json.dumps(cfg))
        csv_path = self.root / "bars.csv"
        with csv_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ts","open","high","low","close","volume"])
            writer.writeheader()
            for i in range(120):
                p = 100 + (i // 12 % 2) * 8 + (i % 12) * (1 if i // 12 % 2 else -1)
                writer.writerow({"ts": f"2026-01-01T{i//60:02d}:{i%60:02d}:00", "open": p, "high": p+1, "low": p-1, "close": p, "volume": 100})
        db = self.root / "bars.sqlite"
        ingest_ohlcv_csv(str(csv_path), "EURUSD", "M1", str(db))
        self.research = prepare_paper_candidates("EURUSD", "M1", str(db), fast=3, slow=7,
                                                  spread=0.2, slippage=0.1, commission=0.5,
                                                  checkpoint_path=self.root/"checkpoint.json",
                                                  telemetry_path=self.root/"research.json")
        self.candidate = next(e for e in self.research["events"] if e["side"] == "BUY")
        self.session = self.root / "session.json"
        self.day = self.root / "day.jsonl"
        self.broker = self.root / "broker.jsonl"
        self.execution = self.root / "execution.jsonl"
        self.manager = PaperTradingSessionManager(str(self.session),str(self.day),str(self.config))
        self.assertEqual(self.manager.open_session()["decision"], "SESSION_OPENED")
        self.gateway = ExecutionGateway(
            ledger_path=str(self.execution),ftmo_config_path=str(self.config),
            paper_session_path=str(self.session),paper_day_ledger_path=str(self.day),
            paper_broker_ledger_path=str(self.broker))
        self.regime = {"regime":"TREND_UP","trade_allowed":True,"normalized_atr":0.005}
        self.genome = {"genome_id":"M8_TEST","regime":"TREND_UP","edge_claim":"NONE"}

    def submit(self, **kwargs):
        params=dict(risk_amount=10.0,stop_distance=1.0,reward_multiple=2.5,
                    regime_report=self.regime,genome=self.genome,
                    authorize_offline_replay=True)
        params.update(kwargs)
        return replay_candidate_to_paper(self.candidate,self.gateway,**params)

    def test_full_research_to_gateway_restart_settle_once(self):
        accepted=self.submit(telemetry_path=self.root/"decision.json")
        self.assertEqual(accepted["decision"],"ACCEPT_SIMULATED_ORDER",accepted)
        self.assertTrue(accepted["reservation_id"])
        self.assertTrue(all(c["ok"] for c in accepted["checks"]))
        self.assertEqual(accepted["mode"],"PAPER")
        self.assertEqual(json.loads((self.root/"decision.json").read_text())["reservation_id"],accepted["reservation_id"])
        restarted=PaperTradingSessionManager(str(self.session),str(self.day),str(self.config))
        self.assertEqual(restarted.reconcile_paper_fills(str(self.broker))["decision"],"BLOCK_UNSETTLED_BROKER_FILL")
        recovery=restarted.recover_interrupted_paper_fills(str(self.broker))
        self.assertEqual(recovery["decision"],"PAPER_FILLS_ACKNOWLEDGED")
        self.assertEqual(restarted.reconcile_paper_fills(str(self.broker))["decision"],"BLOCK_UNSETTLED_BROKER_FILL")
        settled=restarted.settle_paper_order(accepted["reservation_id"],-25.0)
        self.assertEqual(settled["decision"],"PAPER_RESERVATION_SETTLED")
        again=restarted.settle_paper_order(accepted["reservation_id"],-25.0)
        self.assertNotEqual(again["decision"],"PAPER_RESERVATION_SETTLED")
        state=json.loads(self.session.read_text())
        self.assertEqual(state["trades"],1)
        self.assertEqual(state["daily_pnl"],-25.0)
        self.assertEqual(restarted.reconcile_paper_fills(str(self.broker))["decision"],"PAPER_RECONCILIATION_CLEAN")
        duplicate=self.submit()
        self.assertNotEqual(duplicate["decision"],"ACCEPT_SIMULATED_ORDER")

    def test_no_authorization_no_order(self):
        denied=self.submit(authorize_offline_replay=False)
        self.assertEqual(denied["decision"],"BLOCKED_M8_PRECHECK")
        self.assertFalse(self.broker.exists())

    def test_cost_drift_no_order(self):
        modified=dict(self.candidate,costs=dict(self.candidate["costs"],spread=0.3))
        denied=self.submit(candidate=modified) if False else replay_candidate_to_paper(
            modified,self.gateway,risk_amount=10,stop_distance=1,regime_report=self.regime,
            genome=self.genome,authorize_offline_replay=True)
        self.assertEqual(denied["reason"],"COST_CONFIG_DRIFT")
        self.assertFalse(self.broker.exists())

    def test_invalid_risk_no_order(self):
        denied=self.submit(risk_amount=-10)
        self.assertEqual(denied["reason"],"INVALID_PRICE_OR_RISK")
        self.assertFalse(self.broker.exists())

if __name__=="__main__":
    unittest.main()
