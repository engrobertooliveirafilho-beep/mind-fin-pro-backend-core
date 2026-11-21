"""Offline regression for the P2366 institutional targeting engine (PAPER only)."""
import unittest
from app.runtime.p2366_institutional_targeting_engine import institutional_targets


class InstitutionalTargetsRegression(unittest.TestCase):
    def base(self, **overrides):
        ctx = dict(entry=100, stop=98, side="BUY", swing_high=102,
                   swing_low=99, atr=1, session_high=104,
                   session_low=None, liquidity_high=104,
                   liquidity_low=None, vwap=100, round_number=101)
        ctx.update(overrides)
        return ctx

    def test_missing_optional_levels_do_not_crash(self):
        out = institutional_targets(self.base())
        self.assertTrue(out["approved"])
        self.assertGreaterEqual(out["rr"], 2)
        self.assertEqual(out["mode"], "PAPER_ONLY")

    def test_short_with_missing_optional_levels(self):
        out = institutional_targets(self.base(side="SELL", stop=102))
        self.assertTrue(out["approved"])
        self.assertGreaterEqual(out["rr"], 2)

    def test_below_two_r_is_blocked(self):
        out = institutional_targets(self.base(swing_high=100.5, swing_low=99.5,
            atr=0.2, session_high=101, liquidity_high=101, vwap=100, round_number=101))
        self.assertFalse(out["approved"])
        self.assertEqual(out["decision"], "BLOCK_TARGET_BELOW_2R")

    def test_zero_risk_is_blocked(self):
        out = institutional_targets(self.base(stop=100))
        self.assertFalse(out["approved"])

    def test_unknown_side_is_blocked(self):
        out = institutional_targets(self.base(side="HOLD"))
        self.assertFalse(out["approved"])

    def test_nan_is_blocked(self):
        out = institutional_targets(self.base(atr=float("nan")))
        self.assertFalse(out["approved"])
        self.assertEqual(out["decision"], "BLOCK_INVALID_NUMERIC")

    def test_rounded_two_r_must_not_pass(self):
        out = institutional_targets(self.base(swing_high=100, swing_low=100,
            atr=0, session_high=103.999, liquidity_high=103.999,
            vwap=100, round_number=100))
        self.assertFalse(out["approved"])
        self.assertEqual(out["decision"], "BLOCK_TARGET_BELOW_2R")

    def test_buy_stop_above_entry_is_blocked(self):
        out = institutional_targets(self.base(stop=102))
        self.assertFalse(out["approved"])
        self.assertEqual(out["decision"], "BLOCK_INVALID_RISK")

    def test_sell_stop_below_entry_is_blocked(self):
        out = institutional_targets(self.base(side="SELL", stop=98))
        self.assertFalse(out["approved"])
        self.assertEqual(out["decision"], "BLOCK_INVALID_RISK")

    def test_missing_entry_is_blocked(self):
        ctx = self.base()
        del ctx["entry"]
        self.assertEqual(institutional_targets(ctx)["decision"], "BLOCK_INVALID_INPUT")

    def test_missing_stop_is_blocked(self):
        ctx = self.base()
        del ctx["stop"]
        self.assertEqual(institutional_targets(ctx)["decision"], "BLOCK_INVALID_INPUT")

    def test_malformed_stop_is_blocked(self):
        self.assertEqual(institutional_targets(self.base(stop="bad"))["decision"], "BLOCK_INVALID_INPUT")

    def test_no_real_orders(self):
        out = institutional_targets(self.base())
        self.assertEqual(out["real_orders"], "FORBIDDEN")
        self.assertEqual(out["ftmo_real"], "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()
