import tempfile,unittest
from pathlib import Path
from p2400_p2401_audit import inspect,audit
P2400='''import hashlib
from pathlib import Path
ROOT=Path("repo")
module=ROOT/"app"/"runtime"/"p2400.py"
module.write_text("runtime module")
'''
P2401='''import hashlib
def stable_float(seed,low,high):
 h=int(hashlib.sha256(seed.encode()).hexdigest()[:12],16)
 return low+(high-low)*((h%1000000)/1000000)
def evaluate_candidate(c):
 pf=stable_float(c["id"],0.7,2.4)
 wr=stable_float(c["id"],30,70)
 exp=stable_float(c["id"],-0.2,0.3)
 dd=stable_float(c["id"],1.0,7.0)
 samples=int(stable_float(c["id"],22,210))
 passed_windows=int(stable_float(c["id"],1,6))
 return pf,wr,exp,dd,samples,passed_windows
'''
def write_fixture(text):
 f=tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",delete=False,suffix=".py")
 f.write(text);f.close();return Path(f.name)
class AuditTests(unittest.TestCase):
 def setUp(self):
  self.p0=write_fixture(P2400);self.p1=write_fixture(P2401)
 def tearDown(self):
  self.p0.unlink(missing_ok=True);self.p1.unlink(missing_ok=True)
 def test_p2400_runtime_write_detected(self): self.assertTrue(inspect(self.p0)["runtime_write_pattern"])
 def test_p2401_hash_metrics_detected(self): self.assertTrue(inspect(self.p1)["hash_derived_metrics"])
 def test_p2401_has_no_market_data_fields(self): self.assertFalse(inspect(self.p1)["price_or_trade_data_inputs_referenced"])
 def test_p2401_promotions_invalid(self):
  r=audit(self.p0,self.p1);self.assertTrue(r["p2401_metrics_are_synthetic"]);self.assertFalse(r["p2401_promotions_valid"])
 def test_runtime_promotion_blocked(self): self.assertFalse(audit(self.p0,self.p1)["runtime_promotion_allowed"])
if __name__=="__main__":unittest.main()
