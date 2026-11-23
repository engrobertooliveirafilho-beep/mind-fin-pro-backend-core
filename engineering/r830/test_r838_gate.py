import unittest
from r838_gate import audit
class Tests(unittest.TestCase):
 def test_burst(self): self.assertIn(('f','constant_burst'),audit('def f(): return "burst"')['findings'])
 def test_override(self): self.assertIn(('f','answer_override'),audit('def f():\n ans="fixed"')['findings'])
 def test_syntax(self): self.assertEqual(audit('def (')['error'],'syntax')
 def test_no_cert(self): self.assertFalse(audit('def f(): return 1')['certified'])
 def test_synthetic(self): self.assertIn(('f','synthetic_generator_call'),audit('def f(): return train_sim()')['findings'])
if __name__=='__main__':unittest.main()
