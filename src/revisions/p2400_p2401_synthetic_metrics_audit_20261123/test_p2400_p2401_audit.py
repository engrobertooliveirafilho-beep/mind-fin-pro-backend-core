import unittest
from pathlib import Path
from p2400_p2401_audit import inspect,audit
ROOT=Path(__file__).resolve().parents[3]
P2400=ROOT/"p2400_research_space_expansion.py"
P2401=ROOT/"p2401_multi_edge_walk_forward_dd_filter.py"
class AuditTests(unittest.TestCase):
 def test_p2400_runtime_write_detected(self): self.assertTrue(inspect(P2400)["runtime_write_pattern"])
 def test_p2401_hash_metrics_detected(self): self.assertTrue(inspect(P2401)["hash_derived_metrics"])
 def test_p2401_lacks_price_inputs(self): self.assertFalse(inspect(P2401)["price_or_trade_data_inputs_referenced"])
 def test_promotions_invalidated(self):
  r=audit(P2400,P2401);self.assertTrue(r["p2401_metrics_are_synthetic"]);self.assertFalse(r["p2401_promotions_valid"])
 def test_runtime_promotion_blocked(self): self.assertFalse(audit(P2400,P2401)["runtime_promotion_allowed"])
if __name__=="__main__":unittest.main()
