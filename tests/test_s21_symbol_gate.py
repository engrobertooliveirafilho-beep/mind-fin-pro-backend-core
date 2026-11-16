import hashlib
import unittest
from app.runtime.s21_symbol_gate import S21Blocked, admit_paper_decision
SOURCE = b'attested-fixture'
ROW = b'attested-row'
SHA = hashlib.sha256(SOURCE).hexdigest()
BASE = {'symbol':'eurusd','asset':'EURUSD','source_dataset_id':'DATA-1','source_row_hash':hashlib.sha256(ROW).hexdigest(),
        'timestamp_utc':'2026-08-11T12:00:00Z','day':'2026-08-11','tick':1,
        'decision_direction':'HOLD','mode':'PAPER_ONLY','real_orders_allowed':False}
class GateTests(unittest.TestCase):
    def admit(self, **updates):
        return admit_paper_decision({**BASE, **updates},source_bytes=SOURCE,source_sha256=SHA,source_row_bytes=ROW)
    def blocked(self, reason, **updates):
        with self.assertRaisesRegex(S21Blocked,reason):self.admit(**updates)
    def test_valid(self):
        out=self.admit();self.assertEqual(out['symbol'],'EURUSD');self.assertEqual(out['mode'],'PAPER_ONLY');self.assertEqual(len(out['payload_sha256']),64)
    def test_missing_symbol(self):self.blocked('MISSING_SYMBOL',symbol=None)
    def test_invalid_symbol(self):self.blocked('INVALID_SYMBOL',symbol='EUR/USD')
    def test_conflict(self):self.blocked('ASSET_SYMBOL_CONFLICT',asset='XAUUSD')
    def test_missing_dataset(self):self.blocked('MISSING_DATASET_ID',source_dataset_id='')
    def test_bad_row_hash(self):self.blocked('INVALID_SHA256',source_row_hash='bad')
    def test_live(self):self.blocked('PAPER_ONLY_REQUIRED',mode='LIVE')
    def test_real_order(self):self.blocked('PAPER_ONLY_REQUIRED',real_orders_allowed=True)
    def test_day_mismatch(self):self.blocked('DAY_TIMESTAMP_MISMATCH',day='2026-08-12')
    def test_invalid_tick(self):self.blocked('INVALID_TICK',tick=True)
    def test_invalid_direction(self):self.blocked('INVALID_DIRECTION',decision_direction='CLOSE')
    def test_source_tamper(self):
        with self.assertRaisesRegex(S21Blocked,'SOURCE_HASH_MISMATCH'):
            admit_paper_decision(BASE,source_bytes=b'tampered',source_sha256=SHA,source_row_bytes=ROW)
    def test_forged_row_hash(self):
        self.blocked('ROW_HASH_MISMATCH', source_row_hash='0'*64)
    def test_tampered_row_bytes(self):
        with self.assertRaisesRegex(S21Blocked,'ROW_HASH_MISMATCH'):
            admit_paper_decision(BASE,source_bytes=SOURCE,source_sha256=SHA,source_row_bytes=b'tampered')
if __name__=='__main__':unittest.main()
