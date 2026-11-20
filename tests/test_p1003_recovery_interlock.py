import unittest,tempfile,hashlib
from pathlib import Path
from app.runtime.p1003_recovery_interlock import assess,BLOCKS
H={**BLOCKS,'RECOVERY_ACTION':'NONE'}
U={'e2e_certified':False,'order_send_allowed':False,'certification':'BLOCKED_UPSTREAM'}
class Tests(unittest.TestCase):
 def test_upstream_block(self):self.assertEqual(assess(H,U,{})['status'],'BLOCKED')
 def test_never_rerun(self):self.assertFalse(assess(H,U,{})['automatic_rerun_allowed'])
 def test_missing(self):self.assertEqual(len(assess(H,U,{'/nonexistent/eldora':{'sha256':'a'*64}})['missing']),1)
 def test_unsafe(self):
  with self.assertRaises(ValueError):assess({**H,'REAL_ORDERS':'ALLOWED'},U,{})
 def test_upstream_unsafe(self):
  with self.assertRaises(ValueError):assess(H,{**U,'order_send_allowed':True},{})
 def test_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test';p.write_text('modified');self.assertEqual(len(assess(H,U,{str(p):{'sha256':'a'*64}})['altered']),1)
 def test_hash_ok(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test';p.write_text('ok');sha=hashlib.sha256(p.read_bytes()).hexdigest();self.assertEqual(assess(H,{**U,'certification':'CERTIFIED'},{str(p):{'sha256':sha}})['status'],'REVIEW_REQUIRED')
 def test_bad_manifest(self):
  with self.assertRaises(ValueError):assess(H,U,{'a':{'sha256':'bad'}})
