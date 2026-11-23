import unittest
from signal_lineage_gate import validate
H='a'*64
R=dict(edge_id='E1',symbol='GER40',timeframe='M15',signal_id='S1',strategy_source_sha256=H,source_ohlc_sha256=H,signal_time='2026-01-01T10:00:00',entry_time='2026-01-01T10:15:00',exit_time='2026-01-01T10:30:00',side='BUY',pnl_r='0.2',execution_mode='PAPER_ONLY',real_execution_allowed='false')
class TestGate(unittest.TestCase):
 def test_schema_pass_not_certification(self):
  x=validate([R],{'E1'});self.assertTrue(x['schema_valid']);self.assertFalse(x['portfolio_correlation_certified'])
 def test_missing_signal(self):
  r={**R};r.pop('signal_id');self.assertRaises(ValueError,validate,[r],{'E1'})
 def test_wrong_symbol(self):self.assertRaises(ValueError,validate,[{**R,'symbol':'XAUUSD'}],{'E1'})
 def test_future_signal(self):self.assertRaises(ValueError,validate,[{**R,'signal_time':'2026-01-01T10:45:00'}],{'E1'})
 def test_duplicate(self):self.assertRaises(ValueError,validate,[R,R],{'E1'})
 def test_real_orders(self):self.assertRaises(ValueError,validate,[{**R,'execution_mode':'LIVE'}],{'E1'})
 def test_nan(self):self.assertRaises(ValueError,validate,[{**R,'pnl_r':'nan'}],{'E1'})
 def test_invalid_hash(self):self.assertRaises(ValueError,validate,[{**R,'strategy_source_sha256':'123'}],{'E1'})
 def test_empty(self):self.assertRaises(ValueError,validate,[],{'E1'})
if __name__=='__main__':unittest.main()
