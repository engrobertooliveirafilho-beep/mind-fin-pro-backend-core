import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, UTC
from types import SimpleNamespace
from unittest.mock import patch

from mind_trader.app.execution.gateway import ExecutionGateway


class TestP2343GatewayRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "ledger.jsonl"
        self.state = dict(status="OPEN", session_id="s1", loss_streak=1,
                          trades=1, daily_pnl=-10.0)
        self.rows = [
            dict(type="SESSION_OPENED", session_id="s1", event_id="e0"),
            dict(type="TRADE_RESULT", session_id="s1", event_id="e1",
                 pnl=-10.0, trades=1, daily_pnl=-10.0),
        ]
        self.gateway = ExecutionGateway.__new__(ExecutionGateway)
        self.gateway.paper = SimpleNamespace(
            ledger_path=self.path, daily_summary=lambda: dict(self.state))
        self.snapshot = dict(symbol="EURUSD", side="BUY", session_id="s1",
                             evidence_id="fixture-only",
                             observed_at=datetime.now(UTC).isoformat(),
                             context=dict.fromkeys(("m1","m5","m15","h1",
                                 "trend_filter","volatility_filter","session_filter",
                                 "support_resistance_filter"), True))
        self.gateway.trusted_context_provider = lambda *args: self.snapshot
        self.trade = dict(symbol="EURUSD", side="BUY", loss_streak=0)
        self.session = dict(allowed=True, session_id="s1")

    def check(self):
        self.path.write_text("\n".join(json.dumps(r) for r in self.rows), encoding="utf-8")
        return self.gateway._post_loss_check("PAPER", self.trade, self.session)

    def test_consistent_history(self):
        result = self.check()
        self.assertTrue(result["ok"])
        self.assertEqual(result["loss_streak"], 1)
        self.assertEqual(result["ledger_event_id"], "e1")

    def test_pnl_divergence(self):
        self.state["daily_pnl"] = -9
        self.assertFalse(self.check()["ok"])

    def test_duplicate_event(self):
        self.rows[1]["event_id"] = "e0"
        self.assertFalse(self.check()["ok"])

    def test_omitted_loss(self):
        self.state["loss_streak"] = 0
        self.assertFalse(self.check()["ok"])

    def test_missing_trade_event(self):
        self.rows.pop()
        self.assertFalse(self.check()["ok"])

    def test_invalid_context_type(self):
        self.snapshot["context"]["m1"] = 8
        self.assertFalse(self.check()["ok"])

    def test_wrong_symbol(self):
        self.snapshot["symbol"] = "GBPUSD"
        self.assertFalse(self.check()["ok"])

    def test_missing_provider(self):
        self.gateway.trusted_context_provider = None
        self.assertFalse(self.check()["ok"])

    def test_stale_context(self):
        self.snapshot["observed_at"] = "2000-01-01T00:00:00+00:00"
        self.assertFalse(self.check()["ok"])

    def test_gate_rejection(self):
        self.snapshot["context"]["m1"] = False
        self.snapshot["context"]["m5"] = False
        self.assertFalse(self.check()["ok"])

    def test_single_gate_call(self):
        from mind_trader.app.execution import gateway
        with patch.object(gateway, "post_loss_gate", wraps=gateway.post_loss_gate) as gate:
            self.assertTrue(self.check()["ok"])
            gate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
