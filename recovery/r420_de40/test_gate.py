import unittest,hashlib,tempfile
from pathlib import Path
from de40_costed_gate import replay
class Tests(unittest.TestCase):
 def setUp(self):
  import os
  fd,name=tempfile.mkstemp();os.close(fd);self.p=Path(name);self.p.write_text('time;open;high;low;close;spread;symbol;timeframe\n'+''.join(f'2026.01.{i+1:02d} 00:00:00;100;105;95;{100+i%3};50;DE40;D1\n' for i in range(30)));self.h=hashlib.sha256(self.p.read_bytes()).hexdigest()
 def tearDown(self):self.p.unlink()
 def test_hash(self):self.assertEqual(replay(self.p,'0'*64)['reason'],'HASH_MISMATCH')
 def test_contract(self):self.assertEqual(replay(self.p,self.h)['reason'],'COST_AND_FTMO_CONTRACT_REQUIRED')
 def test_costed(self):self.assertEqual(replay(self.p,self.h,point_size=.01,slippage_points=1,ftmo_rules={'max_daily_loss':.05})['status'],'PAPER_COSTED_UNCERTIFIED')
 def test_negative_cost(self):self.assertEqual(replay(self.p,self.h,point_size=-1,slippage_points=1,ftmo_rules={})['reason'],'INVALID_COST_CONTRACT')
 def test_no_ftmo_cert(self):self.assertFalse(replay(self.p,self.h,point_size=.01,slippage_points=1,ftmo_rules={})['ftmo_certified'])
if __name__=='__main__':unittest.main()
