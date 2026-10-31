import tempfile,unittest,hashlib
from pathlib import Path
from recovery.r344_evidence.provenance_gate import verify_file,verify_oos_chronology,evidence_gate

class ProvenanceTest(unittest.TestCase):
 def test_missing_independent_hash_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"data";p.write_bytes(b"test")
   self.assertFalse(verify_file(p,None)["verified"])
 def test_real_sha_match_and_mismatch(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"data";p.write_bytes(b"test")
   self.assertTrue(verify_file(p,hashlib.sha256(b"test").hexdigest())["verified"])
   self.assertFalse(verify_file(p,"0"*64)["verified"])
 def test_chronology_overlap_rejected(self):
  self.assertFalse(verify_oos_chronology("2026-01-02","2026-01-01","2026-01-03"))
  self.assertFalse(verify_oos_chronology("2026-01-02","2026-01-02","2026-01-03"))
  self.assertTrue(verify_oos_chronology("2026-01-01","2026-01-02","2026-01-03"))
 def test_no_automatic_promotion_even_when_basics_pass(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"data";p.write_bytes(b"test")
   r=evidence_gate(p,hashlib.sha256(b"test").hexdigest(),"2026-01-01","2026-01-02","2026-01-03")
   self.assertTrue(r["source"]["verified"])
   self.assertTrue(r["chronology_verified"])
   self.assertFalse(r["certified"])
   self.assertFalse(r["promotion_authorized"])
if __name__=="__main__":unittest.main()
