"""ET665.R358: three historical stubs replaced by distinct offline computations."""
import hashlib,json,unittest
from mind_trader.experimental.et665_r340_safe_agent_dispatch import run_agent
NAMES=("domain_economics_finance_markets","domain_facebook_media_buyer_engine","domain_instagram_brand_engine")
def sha(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class R358RealDomainAgents(unittest.TestCase):
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
        self.assertEqual(results[0]["output"]["operating_margin_pct"],"-200.00")
        self.assertEqual(results[1]["output"]["campaign_status"],"PAUSED")
        self.assertEqual(results[2]["output"]["posts_published"],0)
    def test_reject_modified_input(self):
        p=self.payload();p["revenue"]="2000.00"
        for n in NAMES:
            with self.subTest(agent=n),self.assertRaisesRegex(ValueError,"hash mismatch"):
                run_agent(n,p)
    def test_reject_nan(self):
        p=self.payload();p["revenue"]="NaN"
        p["input_sha256"]=sha({k:v for k,v in p.items() if k!="input_sha256"})
        for n in NAMES:
            with self.subTest(agent=n),self.assertRaises(ValueError):
                run_agent(n,p)
if __name__=="__main__":unittest.main()
