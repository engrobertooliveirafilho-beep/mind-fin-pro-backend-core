import unittest
from dataclasses import replace
from app.runtime.agents_unified_dispatch_safe import dispatch_evidence_gated_agent, AgentDispatchDenied
from app.runtime.trader_agent_evidence_gate import AgentEvidence

class EvidenceDispatch(unittest.TestCase):
    def setUp(self):
        self.calls=[]
        self.e=AgentEvidence('finance',True,True,'healthy',True,True,True,True)
        self.handlers={'finance':lambda p:self.calls.append(('finance',p)) or 'ok',
                       'safety':lambda p:self.calls.append(('safety',p)) or 'wrong'}
    def run_dispatch(self, agent='finance', evidence=None, handlers=None):
        return dispatch_evidence_gated_agent(agent,42,handlers=self.handlers if handlers is None else handlers,
                   evidence_by_id={'finance':self.e} if evidence is None else evidence)
    def test_certified_exact_agent(self):
        self.assertEqual(self.run_dispatch(),'ok')
        self.assertEqual(self.calls,[('finance',42)])
    def test_unknown_health(self):
        with self.assertRaises(AgentDispatchDenied):
            self.run_dispatch(evidence={'finance':replace(self.e,health_status='unknown')})
        self.assertEqual(self.calls,[])
    def test_stub_step_denied(self):
        with self.assertRaises(AgentDispatchDenied):
            self.run_dispatch(evidence={'finance':replace(self.e,steps_implemented=False)})
    def test_missing_human_approval(self):
        with self.assertRaises(AgentDispatchDenied):
            self.run_dispatch(evidence={'finance':replace(self.e,human_approved=False)})
    def test_cross_agent_identity(self):
        with self.assertRaises(AgentDispatchDenied):
            self.run_dispatch(evidence={'finance':replace(self.e,agent_id='safety')})
    def test_missing_handler(self):
        with self.assertRaises(AgentDispatchDenied):
            self.run_dispatch(handlers={})
    def test_unstructured_evidence(self):
        with self.assertRaises(AgentDispatchDenied):
            self.run_dispatch(evidence={'finance':{'agent_id':'finance'}})
    def test_empty_identity(self):
        with self.assertRaises(AgentDispatchDenied):
            self.run_dispatch(agent='')
