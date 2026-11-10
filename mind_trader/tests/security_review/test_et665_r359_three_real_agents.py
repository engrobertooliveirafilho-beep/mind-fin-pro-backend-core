"""ET665.R359: real offline behavior of three candidate agents."""
import hashlib,json,unittest
from mind_trader.experimental.et665_r340_safe_agent_dispatch import run_agent
NAMES=("domain_napoleon_hill_engine","domain_psychology_mindset","domain_social_recommendation_kernel")
def sha(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class R359RealAgents(unittest.TestCase):
    def payload(self):
        d={"component":"monthly_cashflow","revenue":"1000.00","fixed_costs":"2500.00","variable_costs":"500.00","cash_balance":"9000.00"}
        return {**d,"input_sha256":sha(d)}
    def test_real_e2e(self):
        results=[run_agent(n,self.payload()) for n in NAMES]
        self.assertEqual(len({r["output_sha256"] for r in results}),3)
        for r in results:
            self.assertEqual(r["output_sha256"],sha(r["output"]))
            self.assertEqual(r["processed_items"],4)
            self.assertEqual(r["real_orders"],"FORBIDDEN")
            self.assertFalse(r["promotion_authorized"])
        self.assertEqual(results[0]["output"]["gap_to_goal"],"2000.00")
        self.assertIsNone(results[1]["output"]["mental_health_diagnosis"])
        self.assertEqual(results[2]["output"]["ranked_content"][0]["id"],"expense_review")
    def test_tamper(self):
        p=self.payload();p["cash_balance"]="1.00"
        for n in NAMES:
            with self.subTest(agent=n),self.assertRaisesRegex(ValueError,"hash mismatch"):
                run_agent(n,p)
    def test_nonfinite(self):
        p=self.payload();p["revenue"]="NaN"
        p["input_sha256"]=sha({k:v for k,v in p.items() if k!="input_sha256"})
        for n in NAMES:
            with self.subTest(agent=n),self.assertRaises(ValueError):
                run_agent(n,p)
if __name__=="__main__":unittest.main()
