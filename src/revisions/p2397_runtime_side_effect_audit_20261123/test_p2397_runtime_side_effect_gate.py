import unittest
from p2397_runtime_side_effect_gate import audit_source_text
ORIGINAL='''ROOT=Path("repo")\nmodule=ROOT/"app"/"runtime"/"p2397.py"\nmodule.write_text("source")\nsummary={"paper_stack_modified":True}'''
SAFE='''OUT=Path("evidence")\n(OUT/"summary.json").write_text("{}")\nsummary={"paper_stack_modified":False}'''
class P2397AuditTests(unittest.TestCase):
 def test_original_runtime_write_detected(self):
  r=audit_source_text(ORIGINAL);self.assertTrue(r["runtime_mutation_risk"])
 def test_summary_modified_flag_detected(self):
  self.assertTrue(audit_source_text(ORIGINAL)["paper_stack_modified_true"])
 def test_no_mutation_claim_rejected(self):
  self.assertFalse(audit_source_text(ORIGINAL)["historical_no_mutation_claim_supported"])
 def test_evidence_only_write_is_not_runtime_write(self):
  self.assertFalse(audit_source_text(SAFE)["runtime_mutation_risk"])
if __name__=="__main__":unittest.main()
