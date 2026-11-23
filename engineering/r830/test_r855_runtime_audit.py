import unittest
from r855_runtime_audit import audit_runtime
class Tests(unittest.TestCase):
 def test_scheduler(self):self.assertEqual(audit_runtime(b'start_scheduler()')['reason'],'side_effect_calls')
 def test_subprocess(self):self.assertIn('subprocess.run',audit_runtime(b'subprocess.run([])')['findings'])
 def test_copy(self):self.assertIn('shutil.copy',audit_runtime(b'shutil.copy(a,b)')['findings'])
 def test_mkdir(self):self.assertEqual(audit_runtime(b'path.mkdir()')['status'],'blocked')
 def test_write(self):self.assertEqual(audit_runtime(b'path.write_text("x")')['status'],'blocked')
 def test_no_execute(self):self.assertFalse(audit_runtime(b'print("ok")')['execution_authorized'])
 def test_not_certified(self):self.assertFalse(audit_runtime(b'pass')['runtime_certified'])
 def test_empty(self):self.assertEqual(audit_runtime(b'')['reason'],'invalid_source')
 def test_none(self):self.assertEqual(audit_runtime(None)['reason'],'invalid_source')
 def test_unicode(self):self.assertEqual(audit_runtime(b'\xff')['reason'],'invalid_python')
 def test_syntax(self):self.assertEqual(audit_runtime(b'def :')['reason'],'invalid_python')
 def test_candidate(self):self.assertEqual(audit_runtime(b'def run(): return 1')['status'],'candidate_only')
if __name__=='__main__':unittest.main()
