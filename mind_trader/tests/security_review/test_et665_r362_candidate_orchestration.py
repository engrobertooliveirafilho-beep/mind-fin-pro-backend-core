"""ET665.R362: real 19-candidate integration, tampering, deterministic chain."""
import hashlib,json,unittest
from unittest.mock import patch
from mind_trader.experimental.et665_r362_candidate_orchestration import run_pipeline,digest

class R362Orchestration(unittest.TestCase):
    def payload(self):
        p={"component":"monthly_cashflow","revenue":"1000.00","fixed_costs":"2500.00","variable_costs":"500.00","cash_balance":"9000.00"}
        return {**p,"input_sha256":digest(p)}
    def test_19_actual_modules_e2e(self):
        p=self.payload()
        result=run_pipeline(p)
        self.assertEqual(result["candidate_count"],19)
        self.assertEqual(len({r["agent_id"] for r in result["chain"]}),19)
        self.assertEqual(result["chain_sha256"],result["chain"][-1]["chain_sha256"])
        self.assertEqual(result["chain"][0]["predecessor_sha256"],p["input_sha256"])
        for previous,current in zip(result["chain"],result["chain"][1:]):
            self.assertEqual(current["predecessor_sha256"],previous["chain_sha256"])
        self.assertEqual(run_pipeline(p)["chain_sha256"],result["chain_sha256"])
        self.assertEqual(result["hp19_membership"],"NOT_VERIFIED")
        self.assertFalse(result["phase_b_certified"])
        self.assertEqual(result["real_orders"],"FORBIDDEN")
    def test_input_tamper_fail_closed(self):
        p=self.payload();p["cash_balance"]="2.00"
        with self.assertRaisesRegex(ValueError,"hash mismatch"):
            run_pipeline(p)
    def test_module_failure_aborts_pipeline(self):
        p=self.payload()
        with patch("mind_trader.experimental.et665_r362_candidate_orchestration.run_agent",side_effect=RuntimeError("blocked")):
            with self.assertRaisesRegex(RuntimeError,"blocked"):
                run_pipeline(p)
    def test_malformed_result_aborts(self):
        p=self.payload()
        with patch("mind_trader.experimental.et665_r362_candidate_orchestration.run_agent",return_value={"output":{},"output_sha256":"invalid"}):
            with self.assertRaisesRegex(RuntimeError,"lineage violation"):
                run_pipeline(p)
if __name__=="__main__":unittest.main()
