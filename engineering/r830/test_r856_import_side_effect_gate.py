import unittest
from r856_import_side_effect_gate import inspect_import_safety as audit
class Tests(unittest.TestCase):
 def test_scheduler(self):self.assertEqual(audit(b'start_scheduler()')['status'],'blocked')
 def test_scheduler_alias(self):self.assertEqual(audit(b'from x import start_scheduler as go\ngo()')['status'],'blocked')
 def test_subprocess_alias(self):self.assertEqual(audit(b'import subprocess as sp\nsp.run([])')['status'],'blocked')
 def test_write(self):self.assertEqual(audit(b'path.write_text("x")')['status'],'blocked')
 def test_import_open(self):self.assertEqual(audit(b'open("x")')['status'],'blocked')
 def test_exec(self):self.assertEqual(audit(b'exec("x")')['status'],'blocked')
 def test_dynamic(self):self.assertEqual(audit(b'getattr(x, "run")()')['status'],'blocked')
 def test_function_body(self):self.assertEqual(audit(b'def f():\n subprocess.run([])')['status'],'candidate_only')
 def test_decorator(self):self.assertEqual(audit(b'@start_scheduler()\ndef f(): pass')['status'],'blocked')
 def test_default(self):self.assertEqual(audit(b'def f(x=start_scheduler()): pass')['status'],'blocked')
 def test_empty(self):self.assertEqual(audit(b'')['status'],'blocked')
 def test_invalid(self):self.assertEqual(audit(b'def :')['status'],'blocked')
 def test_no_runtime(self):self.assertFalse(audit(b'pass')['runtime_certified'])
 def test_no_execute(self):self.assertFalse(audit(b'pass')['execution_authorized'])
if __name__=='__main__':unittest.main()
