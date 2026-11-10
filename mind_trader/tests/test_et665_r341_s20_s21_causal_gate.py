import unittest
import csv
import hashlib
import tempfile
from pathlib import Path
from mind_trader.scripts.et665_r341_s20_s21_causal_gate import validate, validate_file, validate_file

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

    def test_blank_none_rejected(self): self.reject(price=None)
    def test_padded_decision_id_rejected(self): self.reject(decision_id=' d1')
    def test_uppercase_hash_rejected(self): self.reject(source_sha256='A'*64)
    def test_missing_snapshot_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'sample.csv'
            p.write_text('decision_id,strategy_id,symbol,decision_ts,signal_ts,price_ts,price,source_sha256\\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'expected_sha256_required'): validate_file(p, '')
    def test_mismatched_snapshot_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'sample.csv'
            p.write_text('sample', encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'snapshot_sha256_mismatch'): validate_file(p, '0'*64)
    def test_duplicate_csv_headers_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'sample.csv'
            p.write_text('decision_id,decision_id,strategy_id,symbol,decision_ts,signal_ts,price_ts,price,source_sha256\\nx,y,s1,EURUSD,100,101,102,1.2,'+'a'*64+'\\n',encoding='utf-8')
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError,'duplicate_or_missing_header'): validate_file(p, sha)
    def test_valid_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample.csv'
            with p.open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=list(BASE))
                w.writeheader()
                w.writerow(BASE)
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(validate_file(p,sha)['input_sha256'],sha)

if __name__ == '__main__': unittest.main()
