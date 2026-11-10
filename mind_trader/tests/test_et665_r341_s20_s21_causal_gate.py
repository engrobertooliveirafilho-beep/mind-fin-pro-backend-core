import unittest
from mind_trader.scripts.et665_r341_s20_s21_causal_gate import validate

BASE = dict(decision_id='d1', strategy_id='s1', symbol='EURUSD', decision_ts='100', signal_ts='101', price_ts='102', price='1.2', source_sha256='a'*64)
class TestGate(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate([BASE])['rows'], 1)
    def reject(self, **kwargs):
        with self.assertRaises(ValueError): validate([dict(BASE, **kwargs)])
    def test_missing(self):
        with self.assertRaises(ValueError): validate([{'decision_id':'x'}])
    def test_empty(self):
        with self.assertRaises(ValueError): validate([])
    def test_future_signal(self): self.reject(signal_ts='99')
    def test_lookahead(self): self.reject(price_ts='100')
    def test_zero_price(self): self.reject(price='0')
    def test_nan(self): self.reject(price='nan')
    def test_symbol(self): self.reject(symbol='eurusd')
    def test_hash(self): self.reject(source_sha256='fake')
    def test_duplicate(self):
        with self.assertRaises(ValueError): validate([BASE, BASE])
    def test_nonmonotonic(self):
        with self.assertRaises(ValueError): validate([BASE, dict(BASE,decision_id='d2',decision_ts='90')])
    def test_bad_timestamp(self): self.reject(decision_ts='n/a')
if __name__ == '__main__': unittest.main()
