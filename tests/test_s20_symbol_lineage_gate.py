import unittest
from s20_symbol_lineage_gate import validate_decision, append_immutable, digest

def row(**kw):
    r = dict(day='2026-08-07', tick='1', symbol='EURUSD', timestamp_utc='2026-08-07T00:00:00Z', source_dataset_id='MT5-1', source_row_hash='a'*64, mode='PAPER_ONLY', real_execution_allowed=False)
    r.update(kw)
    return r

class TestLineage(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate_decision(row())['symbol'], 'EURUSD')
    def test_missing_symbol(self):
        with self.assertRaises(ValueError): validate_decision(row(symbol=''))
    def test_missing_source(self):
        with self.assertRaises(ValueError): validate_decision(row(source_row_hash=''))
    def test_real_forbidden(self):
        with self.assertRaises(ValueError): validate_decision(row(mode='REAL'))
    def test_real_flag_forbidden(self):
        with self.assertRaises(ValueError): validate_decision(row(real_execution_allowed=True))
    def test_duplicate(self):
        with self.assertRaises(ValueError): append_immutable((row(),),row())
    def test_immutable(self):
        original = [row()]; other=row(tick='2'); out=append_immutable(original,other)
        self.assertEqual(len(original),1); self.assertEqual(len(out),2)
    def test_deterministic_hash(self): self.assertEqual(digest([row()]),digest([row()]))
    def test_invalid_symbol(self):
        with self.assertRaises(ValueError): validate_decision(row(symbol='EUR USD'))
    def test_invalid_row(self):
        with self.assertRaises(ValueError): validate_decision(None)

if __name__ == '__main__': unittest.main()
