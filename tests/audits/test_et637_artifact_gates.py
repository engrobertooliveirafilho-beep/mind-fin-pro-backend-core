"""ET-637: fail-closed contract for recovered P2279F/H/I metadata.

This audit does not promote historical edges or invoke an execution adapter.
Run: python -m unittest discover -s tests/audits -p 'test_et637_artifact_gates.py'
"""
import unittest

HISTORICAL_POLICY = {
    "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN",
    "approved_edges": 11, "max_trades_day": 6,
    "max_trades_edge_day": 2, "daily_loss_limit_pct": 1.0,
    "total_loss_limit_pct": 5.0, "default_lot": 0.01,
}
HISTORICAL_LOSS = {"total_trades": 881, "total_losses": 539,
                   "avoidable_loss_candidates": 539, "mode": "PAPER_ONLY",
                   "real_orders": "FORBIDDEN"}
HISTORICAL_WIN = {"total_trades": 881, "total_wins": 342,
                  "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN"}


def validate_historical_artifacts(policy, loss, win):
    """Validate metadata only; never return permission to trade."""
    if any(obj.get("mode") != "PAPER_ONLY" or obj.get("real_orders") != "FORBIDDEN"
           for obj in (policy, loss, win)):
        raise ValueError("Real-order authorization forbidden")
    if policy.get("approved_edges") != 11:
        raise ValueError("Historical edge count mismatch")
    if not (0 < policy.get("daily_loss_limit_pct", 0) <= 1.0
            and 0 < policy.get("total_loss_limit_pct", 0) <= 5.0):
        raise ValueError("Risk bounds exceed audited historical policy")
    if not (0 < policy.get("max_trades_day", 0) <= 6
            and 0 < policy.get("max_trades_edge_day", 0) <= 2):
        raise ValueError("Trade count bounds exceed historical policy")
    if loss.get("total_trades") != win.get("total_trades"):
        raise ValueError("Inconsistent trade totals")
    if loss.get("total_losses", -1) + win.get("total_wins", -1) != loss["total_trades"]:
        raise ValueError("Win/loss partition mismatch")
    if loss.get("avoidable_loss_candidates", 0) > loss["total_losses"]:
        raise ValueError("Invalid avoidable-loss count")
    return {"metadata_consistent": True, "execution_authorized": False,
            "ftmo_certified": False, "monetary_pnl_certified": False}


class ET637ArtifactGateTests(unittest.TestCase):
    def test_original_metadata_consistency(self):
        result = validate_historical_artifacts(HISTORICAL_POLICY, HISTORICAL_LOSS, HISTORICAL_WIN)
        self.assertTrue(result["metadata_consistent"])
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["ftmo_certified"])

    def test_reject_real_orders(self):
        policy = dict(HISTORICAL_POLICY, real_orders="ALLOWED")
        with self.assertRaises(ValueError):
            validate_historical_artifacts(policy, HISTORICAL_LOSS, HISTORICAL_WIN)

    def test_reject_optimistic_reclassification_of_breakeven(self):
        win = dict(HISTORICAL_WIN, total_wins=343)
        with self.assertRaises(ValueError):
            validate_historical_artifacts(HISTORICAL_POLICY, HISTORICAL_LOSS, win)

    def test_reject_loosened_daily_loss(self):
        policy = dict(HISTORICAL_POLICY, daily_loss_limit_pct=2.0)
        with self.assertRaises(ValueError):
            validate_historical_artifacts(policy, HISTORICAL_LOSS, HISTORICAL_WIN)

    def test_reject_inconsistent_trade_count(self):
        loss = dict(HISTORICAL_LOSS, total_trades=880)
        with self.assertRaises(ValueError):
            validate_historical_artifacts(HISTORICAL_POLICY, loss, HISTORICAL_WIN)


if __name__ == "__main__":
    unittest.main()
