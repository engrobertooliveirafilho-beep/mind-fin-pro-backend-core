import tempfile,unittest
from pathlib import Path
from p2402_upstream_gate import certify
SRC='''import pathlib
P2401="P2401_MULTI_EDGE_WALK_FORWARD_DD_FILTER"
def quality_score(e):
 pf=e["pf"]; wr=e["winrate"]; exp=e["expectancy"]; dd=e["max_dd_r"]; n=e["samples"]; w=e["passed_windows"]
 return pf+wr+exp-dd+n+w
module=pathlib.Path("app")/"runtime"/"p2402.py"
module.write_text("runtime")
'''
class Tests(unittest.TestCase):
 def test_detects_invalid_upstream(self):
  with tempfile.NamedTemporaryFile("w",suffix=".py",delete=False) as f:f.write(SRC);p=Path(f.name)
  try:
   r=certify(p);self.assertTrue(r["upstream_performance_invalidated"]);self.assertTrue(r["runtime_write_present"])
  finally:p.unlink()
 def test_performance_never_certified(self):
  with tempfile.NamedTemporaryFile("w",suffix=".py",delete=False) as f:f.write(SRC);p=Path(f.name)
  try:
   r=certify(p);self.assertFalse(r["p2402_performance_certified"]);self.assertFalse(r["selected_pool_performance_valid"])
  finally:p.unlink()
 def test_correlation_and_runtime_blocked(self):
  with tempfile.NamedTemporaryFile("w",suffix=".py",delete=False) as f:f.write(SRC);p=Path(f.name)
  try:
   r=certify(p);self.assertFalse(r["correlation_valid"]);self.assertFalse(r["runtime_promotion_allowed"])
  finally:p.unlink()
if __name__=="__main__":unittest.main()
