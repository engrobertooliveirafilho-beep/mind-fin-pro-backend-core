import unittest
from dataclasses import replace
from app.runtime.trader_agent_evidence_gate import AgentEvidence, certify_paper_agent

class AgentGateTests(unittest.TestCase):
    def setUp(self):
        self.e=AgentEvidence('domain.economics_finance_markets',True,True,'unknown',False,False,False,False)
    def test_registry_only_denied(self): self.assertFalse(certify_paper_agent(self.e))
    def test_missing_steps_denied(self): self.assertFalse(certify_paper_agent(replace(self.e,health_status='healthy',offline_tests_passed=True,paper_integration_passed=True,human_approved=True)))
    def test_missing_paper_integration_denied(self): self.assertFalse(certify_paper_agent(replace(self.e,health_status='healthy',steps_implemented=True,offline_tests_passed=True,human_approved=True)))
    def test_human_approval_required(self): self.assertFalse(certify_paper_agent(replace(self.e,health_status='healthy',steps_implemented=True,offline_tests_passed=True,paper_integration_passed=True)))
    def test_complete_evidence_only(self): self.assertTrue(certify_paper_agent(replace(self.e,health_status='healthy',steps_implemented=True,offline_tests_passed=True,paper_integration_passed=True,human_approved=True)))
    def test_string_flag_rejected(self):
        with self.assertRaises(ValueError): certify_paper_agent(replace(self.e,offline_tests_passed='PASS'))
    def test_empty_id_rejected(self):
        with self.assertRaises(ValueError): certify_paper_agent(replace(self.e,agent_id=''))
    def test_unstructured_rejected(self):
        with self.assertRaises(ValueError): certify_paper_agent({})
