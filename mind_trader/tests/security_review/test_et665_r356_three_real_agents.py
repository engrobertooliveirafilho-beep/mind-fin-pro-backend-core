"""ET665.R356: actual distinct modules, no mocked agents."""
import hashlib
import json
import unittest
from mind_trader.experimental.et665_r340_safe_agent_dispatch import run_agent

NAMES=("cognition_os_kernel_agent","core_high_governance_council","core_safety_compliance_hub")

def sha(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

class RealAgents(unittest.TestCase):
    def payload(self):
        x={"component":"monthly_cashflow","revenue":"1000.00","fixed_costs":"2500.00","variable_costs":"500.00","cash_balance":"9000.00"}
        return {**x,"input_sha256":sha(x)}

    def test_three_distinct_real_outputs(self):
        p=self.payload()
        results=[run_agent(n,p) for n in NAMES]
        self.assertEqual(len({r["agent_id"] for r in results}),3)
        self.assertEqual(len({r["output_sha256"] for r in results}),3)
        for r in results:
            self.assertEqual(r["output_sha256"],sha(r["output"]))
            self.assertEqual(r["processed_items"],4)
            self.assertFalse(r["promotion_authorized"])
            self.assertEqual(r["real_orders"],"FORBIDDEN")
        self.assertEqual(results[0]["output"]["plan"],"preserve_cash")
        self.assertEqual(results[1]["output"]["consensus"],"REVIEW_REQUIRED")
        self.assertEqual(results[2]["output"]["compliance_status"],"REVIEW_REQUIRED")

    def test_reject_tampering_all_three(self):
        p=self.payload()
        p["revenue"]="999.00"
        for name in NAMES:
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,"hash mismatch"):
                run_agent(name,p)

    def test_reject_nonfinite_all_three(self):
        p=self.payload()
        p["revenue"]="NaN"
        p["input_sha256"]=sha({k:v for k,v in p.items() if k!="input_sha256"})
        for name in NAMES:
            with self.subTest(name=name),self.assertRaises(ValueError):
                run_agent(name,p)

if __name__=="__main__":
    unittest.main()
