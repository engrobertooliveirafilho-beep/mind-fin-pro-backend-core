import json,unittest
from pathlib import Path
from lineage_gate import validate
M=json.loads(Path(__file__).with_name("lineage_manifest.json").read_text())
class LineageTests(unittest.TestCase):
 def test_source_metadata_reconciled(self): self.assertTrue(validate(M)["metadata_reconciled"])
 def test_event_count_mismatch_blocks(self):
  x=json.loads(json.dumps(M));x["observed"]["source_edge_event_rows"]=151
  self.assertFalse(validate(x)["metadata_reconciled"])
 def test_fill_claim_remains_false(self):
  x=json.loads(json.dumps(M));x["limits"]["event_rows_are_fills"]=True
  self.assertFalse(validate(x)["metadata_reconciled"])
 def test_p2400_ancestry_not_claimed(self): self.assertFalse(validate(M)["portfolio_correlation_certified"])
 def test_runtime_stays_blocked(self): self.assertFalse(validate(M)["runtime_promotion_allowed"])
if __name__=="__main__":unittest.main()
