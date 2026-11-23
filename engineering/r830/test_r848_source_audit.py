import hashlib, unittest
from r848_source_audit import audit_agent_source
ORIGINAL=b'def run_dry():\n return {"status":"stub","mode":"not_implemented"}\n'
H=hashlib.sha256(ORIGINAL).hexdigest()
class TestAudit(unittest.TestCase):
 def test_original_blocked(self): self.assertEqual(audit_agent_source(ORIGINAL,H)['reason'],'stub_markers')
 def test_markers(self): self.assertEqual(audit_agent_source(ORIGINAL,H)['markers'],['not_implemented','stub'])
 def test_tamper(self): self.assertEqual(audit_agent_source(ORIGINAL+b'x',H)['reason'],'digest_mismatch')
 def test_invalid_source(self): self.assertEqual(audit_agent_source(None,H)['reason'],'invalid_source')
 def test_empty(self): self.assertEqual(audit_agent_source(b'',H)['reason'],'invalid_source')
 def test_invalid_hash(self): self.assertEqual(audit_agent_source(ORIGINAL,None)['reason'],'invalid_digest')
 def test_invalid_python(self):
  b=b'def foo(:'; self.assertEqual(audit_agent_source(b,hashlib.sha256(b).hexdigest())['reason'],'invalid_python')
 def test_no_entry(self):
  b=b'x=1'; self.assertEqual(audit_agent_source(b,hashlib.sha256(b).hexdigest())['reason'],'no_entrypoint')
 def test_candidate_not_certified(self):
  b=b'def run_dry():\n return 42\n'; self.assertFalse(audit_agent_source(b,hashlib.sha256(b).hexdigest())['runtime_certified'])
 def test_unicode(self):
  b=b'\xff'; self.assertEqual(audit_agent_source(b,hashlib.sha256(b).hexdigest())['reason'],'invalid_python')
if __name__=='__main__':unittest.main()
