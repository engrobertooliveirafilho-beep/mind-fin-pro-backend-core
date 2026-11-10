"""ET665.R352 real module integration, no mocked agents."""
import hashlib
import json
import unittest

from app.agents.business_strategy_cashflow_agent import run_dry
from mind_trader.experimental.et665_r340_safe_agent_dispatch import run_agent

def sha(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

class CashflowRealModule(unittest.TestCase):
    def payload(self):
        source={"component":"monthly_cashflow","revenue":"1000.00",
                "fixed_costs":"2500.00","variable_costs":"500.00",
                "cash_balance":"9000.00"}
        return {**source,"input_sha256":sha(source)}

    def test_real_agent_end_to_end(self):
        payload=self.payload()
        result=run_agent("business_strategy_cashflow_agent",payload)
        self.assertEqual(result["output"]["net_cashflow"],"-2000.00")
        self.assertEqual(result["output"]["runway_months"],"4.50")
        self.assertEqual(result["processed_items"],4)
        self.assertEqual(result["output_sha256"],sha(result["output"]))
        self.assertEqual(result["real_orders"],"FORBIDDEN")

    def test_reject_tampered_input(self):
        payload=self.payload()
        payload["revenue"]="999999.00"
        with self.assertRaisesRegex(ValueError,"hash mismatch"):
            run_agent("business_strategy_cashflow_agent",payload)

    def test_reject_nonfinite(self):
        payload=self.payload()
        payload["revenue"]="NaN"
        payload["input_sha256"]=sha({k:v for k,v in payload.items() if k!="input_sha256"})
        with self.assertRaises(ValueError):
            run_agent("business_strategy_cashflow_agent",payload)

if __name__=="__main__":
    unittest.main()
