"""ET665.R363: real dependency and fail-closed adversarial coverage."""
import unittest
from unittest.mock import patch
from mind_trader.experimental.et665_r363_dependent_workflow import run_dependent_workflow
from app.agents._et665_r356_common import digest
from mind_trader.experimental.et665_r340_safe_agent_dispatch import run_agent as actual_run_agent

def payload(revenue="1000.00"):
    p={"component":"monthly_cashflow","revenue":revenue,"fixed_costs":"2500.00","variable_costs":"500.00","cash_balance":"9000.00"}
    return {**p,"input_sha256":digest(p)}

class R363(unittest.TestCase):
    def test_deficit_blocks_spend(self):
        r=run_dependent_workflow(payload())
        self.assertEqual(r["creative"]["recommendation"],"HOLD_SPEND")
        self.assertTrue(r["risk"]["blocked"])
        self.assertEqual(r["final_sha256"],digest(r["creative"]))
        self.assertFalse(r["promotion_authorized"])
    def test_surplus_requires_review(self):
        r=run_dependent_workflow(payload("10000.00"))
        self.assertEqual(r["creative"]["recommendation"],"REVIEW_ONLY")
        self.assertFalse(r["risk"]["blocked"])
        self.assertTrue(r["creative"]["human_approval_required"])
    def test_tampered_input_fails(self):
        p=payload();p["revenue"]="999999.00"
        with self.assertRaises(ValueError):
            run_dependent_workflow(p)
    def test_malicious_creative_objective_fails(self):
        def malicious(name,p):
            result=actual_run_agent(name,p)
            if name=="creative_sora_marketing_director":
                result["output"]["brief"]["objective"]="sustainable_growth"
                result["output_sha256"]=digest(result["output"])
            return result
        with patch("mind_trader.experimental.et665_r363_dependent_workflow.run_agent",side_effect=malicious):
            with self.assertRaisesRegex(RuntimeError,"violates finance risk gate"):
                run_dependent_workflow(payload())
    def test_forged_agent_hash_fails(self):
        def malicious(name,p):
            result=actual_run_agent(name,p)
            if name=="core_safety_compliance_hub":
                result["output_sha256"]="forged"
            return result
        with patch("mind_trader.experimental.et665_r363_dependent_workflow.run_agent",side_effect=malicious):
            with self.assertRaisesRegex(RuntimeError,"lineage violation"):
                run_dependent_workflow(payload())
if __name__=="__main__":unittest.main()
