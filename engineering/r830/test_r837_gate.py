import unittest
from r837_gate import audit,duplicate_groups
class TestGate(unittest.TestCase):
 def test_syntax(self): self.assertEqual(audit('def (')['error'],'syntax')
 def test_no_certification(self): self.assertFalse(audit('def f(): return 1')['certified'])
 def test_functions(self): self.assertEqual(audit('def f(): return 1')['functions'],['f'])
 def test_burst(self): self.assertIn(('f','constant_burst'),audit('def f(): return "burst"')['findings'])
 def test_override(self): self.assertIn(('f','answer_override'),audit('def f():\n ans="fixed"')['findings'])
 def test_duplicate(self): self.assertEqual(duplicate_groups({'a':'x','b':'x','c':'y'}),[['a','b']])
 def test_no_duplicate(self): self.assertEqual(duplicate_groups({'a':'x','b':'y'}),[])
 def test_synthetic(self): self.assertIn(('f','synthetic_generator_call'),audit('def f(): return train_sim()')['findings'])
if __name__=='__main__':unittest.main()
