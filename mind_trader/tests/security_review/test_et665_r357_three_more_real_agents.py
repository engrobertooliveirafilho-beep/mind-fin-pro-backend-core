"""ET665.R357 integration of three real offline agents."""
import hashlib,json,unittest
from mind_trader.experimental.et665_r340_safe_agent_dispatch import run_agent
NAMES=("core_system_supervisor","creative_sora_marketing_director","creative_video_scenarios_agent")
def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class RealR357(unittest.TestCase):
    def payload(self):
        d={"component":"monthly_cashflow","revenue":"1000.00","fixed_costs":"2500.00","variable_costs":"500.00","cash_balance":"9000.00"}
        return {**d,"input_sha256":digest(d)}
    def test_end_to_end(self):
        p=self.payload()
        r=[run_agent(n,p) for n in NAMES]
        self.assertEqual(len({x["output_sha256"] for x in r}),3)
        for x in r:
            self.assertEqual(x["output_sha256"],digest(x["output"]))
            self.assertEqual(x["processed_items"],4)
            self.assertEqual(x["real_orders"],"FORBIDDEN")
            self.assertFalse(x["promotion_authorized"])
        self.assertEqual(r[0]["output"]["health"],"DEGRADED")
        self.assertFalse(r[1]["output"]["generation_executed"])
        self.assertFalse(r[2]["output"]["video_rendered"])
    def test_tamper(self):
        p=self.payload();p["cash_balance"]="999.00"
        for n in NAMES:
            with self.subTest(agent=n),self.assertRaisesRegex(ValueError,"hash mismatch"):
                run_agent(n,p)
    def test_nonfinite(self):
        p=self.payload();p["revenue"]="Infinity"
        p["input_sha256"]=digest({k:v for k,v in p.items() if k!="input_sha256"})
        for n in NAMES:
            with self.subTest(agent=n),self.assertRaises(ValueError):
                run_agent(n,p)
if __name__=="__main__":unittest.main()
