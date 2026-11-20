import tempfile, unittest
from pathlib import Path
from app.runtime.p1630_market_structure_gate import audit, audit_file

class TestP1630(unittest.TestCase):
    def test_valid(self):self.assertEqual(audit({'A':1})['observations'],1)
    def test_no_orders(self):self.assertFalse(audit({'A':1})['order_send_allowed'])
    def test_no_promotion(self):self.assertFalse(audit({'A':1})['promotion_allowed'])
    def test_no_e2e(self):self.assertFalse(audit({'A':1})['e2e_certified'])
    def test_empty(self):
        with self.assertRaises(ValueError):audit({})
    def test_negative(self):
        with self.assertRaises(ValueError):audit({'A':-1})
    def test_float(self):
        with self.assertRaises(ValueError):audit({'A':1.0})
    def test_bool(self):
        with self.assertRaises(ValueError):audit({'A':True})
    def test_blank(self):
        with self.assertRaises(ValueError):audit({'':1})
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{"A":1,"A":2}')
            with self.assertRaises(ValueError):audit_file(p)
    def test_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{"A":NaN}')
            with self.assertRaises(ValueError):audit_file(p)
    def test_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{"A":1}')
            self.assertEqual(len(audit_file(p)['source_sha256']),64)
