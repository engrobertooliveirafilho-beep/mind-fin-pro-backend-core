import unittest
from mind_trader.experimental.et665_r379_original_dispatch_audit import audit,check_dispatch_source,HISTORICAL_DISPATCH
class R379(unittest.TestCase):
    def test_historical_lookup_is_global(self):
        self.assertTrue(check_dispatch_source(HISTORICAL_DISPATCH)["global_run_dry_lookup"])
    def test_duplicate_imports_are_detected(self):
        source="from app.agents.a import run_dry\nfrom app.agents.b import run_dry\n"+HISTORICAL_DISPATCH
        self.assertTrue(check_dispatch_source(source)["collision_risk"])
    def test_safe_distinct_imports(self):
        source="from app.agents.a import run_dry as a\nfrom app.agents.b import run_dry as b\n"+HISTORICAL_DISPATCH
        self.assertFalse(check_dispatch_source(source)["collision_risk"])
    def test_fail_closed_status(self):
        r=audit()
        self.assertEqual(r["official_hp19_certified"],0)
        self.assertEqual(r["phase_b_certified"],0)
        self.assertEqual(r["real_orders"],"FORBIDDEN")
if __name__=="__main__":unittest.main()
