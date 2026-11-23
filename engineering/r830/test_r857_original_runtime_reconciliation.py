import unittest
from r857_original_runtime_reconciliation import audit_recovered
S={'agents_runtime':b'from app.meta.agents_scheduler import start_scheduler\ntry:\n start_scheduler()\nexcept Exception: pass','dev_runtime':b'from pathlib import Path\nREPORTS_DIR=Path("reports")\nREPORTS_DIR.mkdir(parents=True,exist_ok=True)\ndef apply_dev_patches():\n import subprocess,shutil\n subprocess.run(["git","apply"])\n shutil.copy("a","b")','scheduler':b'def start_scheduler():\n import threading\n threading.Thread(target=lambda:None).start()'}
class Tests(unittest.TestCase):
 def test_audited(self):self.assertEqual(audit_recovered(S)['status'],'audited_only')
 def test_autostart(self):self.assertEqual(audit_recovered(S)['reports']['agents_runtime']['status'],'blocked')
 def test_mkdir(self):self.assertEqual(audit_recovered(S)['reports']['dev_runtime']['status'],'blocked')
 def test_scheduler_candidate(self):self.assertEqual(audit_recovered(S)['reports']['scheduler']['status'],'candidate_only')
 def test_no_runtime(self):self.assertFalse(audit_recovered(S)['runtime_certified'])
 def test_no_integration(self):self.assertFalse(audit_recovered(S)['integration_authorized'])
 def test_missing(self):self.assertEqual(audit_recovered({})['status'],'blocked')
 def test_extra(self):self.assertEqual(audit_recovered(dict(S,other=b'pass'))['status'],'blocked')
 def test_bad_type(self):self.assertEqual(audit_recovered(None)['status'],'blocked')
 def test_bad_bytes(self):self.assertEqual(audit_recovered(dict(S,dev_runtime=None))['reports']['dev_runtime']['status'],'blocked')
if __name__=='__main__':unittest.main()
