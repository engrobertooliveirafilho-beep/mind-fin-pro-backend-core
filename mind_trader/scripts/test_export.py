import unittest,tempfile,csv,hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from p2279b2_direct_mt5_export import export,resolve_symbol
class TestExport(unittest.TestCase):
 def test_alias(self):
  self.assertIsNone(resolve_symbol('US100',['USTEC','NAS100']))
  self.assertIsNone(resolve_symbol('EURUSD',['EURUSD_fake']))
  self.assertEqual(resolve_symbol('US100',['USTEC']),'USTEC')
 def test_export(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); m=Mock(); m.symbols_get.return_value=[SimpleNamespace(name='AUDUSD')]; m.copy_rates_from_pos.return_value=[dict(time=1700000000,open=1,high=2,low=1,close=2,tick_volume=3,spread=1,real_volume=0)]
   rows=export(m,p/'out',p/'ev'); self.assertEqual(len(rows),65); self.assertEqual(m.copy_rates_from_pos.call_count,5); self.assertTrue(all(c.args[2]==1 for c in m.copy_rates_from_pos.call_args_list)); m.shutdown.assert_called_once()
   saved=[r for r in rows if r[3]=='RAW_SAVED']; self.assertEqual(len(saved),5)
   for r in saved: self.assertEqual(r[7],hashlib.sha256(Path(r[5]).read_bytes()).hexdigest())
   rows2=export(m,p/'out',p/'ev2'); self.assertEqual(sum(r[3]=='EXISTS_BLOCKED' for r in rows2),5)
   with self.assertRaises(FileExistsError): export(m,p/'out',p/'ev')
   self.assertEqual(m.shutdown.call_count,3)
if __name__=='__main__': unittest.main()
