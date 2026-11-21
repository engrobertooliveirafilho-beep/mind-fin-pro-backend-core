import unittest
from app.runtime.p2366_institutional_targeting_engine import institutional_targets


class P2366AdversarialTests(unittest.TestCase):
    def test_invalid_side_always_forbids_real(self):
        r = institutional_targets({"side":"HOLD","entry":100,"stop":99})
        self.assertFalse(r["approved"])
        self.assertEqual(r["ftmo_real"], "FORBIDDEN")

    def test_overflowed_risk_blocks(self):
        r = institutional_targets({"side":"BUY","entry":1.7e308,"stop":1e-10})
        self.assertFalse(r["approved"])
        self.assertEqual(r["ftmo_real"], "FORBIDDEN")

    def test_negative_atr_blocks(self):
        r = institutional_targets({"side":"BUY","entry":100,"stop":99,"atr":-1})
        self.assertFalse(r["approved"])

    def test_nonpositive_entry_blocks(self):
        r = institutional_targets({"side":"SELL","entry":-1,"stop":-0.5})
        self.assertFalse(r["approved"])

    def test_boolean_numeric_fields_block(self):
        base = {"side": "BUY", "entry": 100, "stop": 99, "atr": 1}
        for field in ("entry", "stop", "atr", "swing_high", "liquidity_low"):
            with self.subTest(field=field):
                result = institutional_targets(dict(base, **{field: True}))
                self.assertFalse(result["approved"])
                self.assertEqual(result["real_orders"], "FORBIDDEN")
                self.assertEqual(result["ftmo_real"], "FORBIDDEN")

    def test_extreme_target_overflow_blocks(self):
        r = institutional_targets({"side":"BUY","entry":100,"stop":99,
                                   "swing_high":1.7e308,"swing_low":0})
        self.assertFalse(r["approved"])
        self.assertEqual(r["decision"], "BLOCK_NUMERIC_OVERFLOW")


if __name__ == "__main__":
    unittest.main()
