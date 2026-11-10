"""ET665.R360: six independent real offline candidate modules."""
import hashlib,json,unittest
from mind_trader.experimental.et665_r340_safe_agent_dispatch import run_agent
NAMES=("domain_tiktok_growth_engine","domain_youtube_longform_engine","meta_autonomous_evolution_agent","meta_global_agent_mapper","meta_mind_archives_agent_mapper","mission_autonomous_docking_agent")
def sha(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class R360RealAgents(unittest.TestCase):
    def payload(self):
        d={"component":"monthly_cashflow","revenue":"1000.00","fixed_costs":"2500.00","variable_costs":"500.00","cash_balance":"9000.00"}
        return {**d,"input_sha256":sha(d)}
    def test_real_e2e(self):
        results=[run_agent(n,self.payload()) for n in NAMES]
        self.assertEqual(len({r["output_sha256"] for r in results}),6)
        for r in results:
            self.assertEqual(r["output_sha256"],sha(r["output"]))
            self.assertEqual(r["processed_items"],4)
            self.assertEqual(r["real_orders"],"FORBIDDEN")
            self.assertFalse(r["promotion_authorized"])
        self.assertEqual(results[0]["output"]["videos_published"],0)
        self.assertEqual(results[1]["output"]["uploads"],0)
        self.assertTrue(results[2]["output"]["gap_detected"])
        self.assertEqual(results[3]["output"]["coverage_count"],3)
        self.assertFalse(results[4]["output"]["drive_or_supabase_accessed"])
        self.assertFalse(results[5]["output"]["docking_executed"])
    def test_reject_tampered(self):
        p=self.payload();p["cash_balance"]="1.00"
        for n in NAMES:
            with self.subTest(agent=n),self.assertRaisesRegex(ValueError,"hash mismatch"):
                run_agent(n,p)
    def test_reject_nonfinite(self):
        p=self.payload();p["revenue"]="NaN"
        p["input_sha256"]=sha({k:v for k,v in p.items() if k!="input_sha256"})
        for n in NAMES:
            with self.subTest(agent=n),self.assertRaises(ValueError):
                run_agent(n,p)
if __name__=="__main__":unittest.main()
