import json,unittest
from unittest.mock import patch
from p2397_historical_bridge import HERE,evaluate_historical_research
class PaperStackTests(unittest.TestCase):
 def test_paper_stack_mismatch_rejected(self):
  p=json.loads((HERE/'p2394_original_summary.json').read_text())
  policy=json.loads((HERE/'p2397_original_policy.json').read_text())
  summary=json.loads((HERE/'p2397_original_summary.json').read_text())
  summary['paper_stack_modified']=False
  with patch('p2397_historical_bridge.json.loads',side_effect=[p,policy,summary]):
   result=evaluate_historical_research()
  self.assertEqual(result.decision,'BLOCK')
  self.assertFalse(result.allowed_for_runtime)
