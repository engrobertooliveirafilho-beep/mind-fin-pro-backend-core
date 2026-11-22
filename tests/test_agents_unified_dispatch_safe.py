import unittest
from app.runtime.agents_unified_dispatch_safe import dispatch_paper_agent, AgentDispatchDenied

class Dispatch(unittest.TestCase):
    def setUp(self):
        self.calls=[]
        self.handlers={'finance.agent':lambda p:self.calls.append(('finance',p)) or 'finance',
                       'safety.agent':lambda p:self.calls.append(('safety',p)) or 'safety'}
    def test_denies_uncertified(self):
        with self.assertRaises(AgentDispatchDenied): dispatch_paper_agent('finance.agent',{},handlers=self.handlers,certified_ids=frozenset())
        self.assertEqual(self.calls,[])
    def test_exact_finance(self):
        self.assertEqual(dispatch_paper_agent('finance.agent',42,handlers=self.handlers,certified_ids=frozenset({'finance.agent'})),'finance')
        self.assertEqual(self.calls,[('finance',42)])
    def test_exact_safety(self):
        self.assertEqual(dispatch_paper_agent('safety.agent',13,handlers=self.handlers,certified_ids=frozenset({'safety.agent'})),'safety')
        self.assertEqual(self.calls,[('safety',13)])
    def test_unknown_denied(self):
        with self.assertRaises(AgentDispatchDenied): dispatch_paper_agent('missing',None,handlers=self.handlers,certified_ids=frozenset({'missing'}))
    def test_empty_denied(self):
        with self.assertRaises(AgentDispatchDenied): dispatch_paper_agent('',None,handlers=self.handlers,certified_ids=frozenset({''}))
    def test_wrong_certification_type_denied(self):
        with self.assertRaises(AgentDispatchDenied): dispatch_paper_agent('finance.agent',None,handlers=self.handlers,certified_ids={'finance.agent'})
    def test_no_implicit_fallback(self):
        with self.assertRaises(AgentDispatchDenied): dispatch_paper_agent('finance.agents',None,handlers=self.handlers,certified_ids=frozenset({'finance.agents'}))
        self.assertEqual(self.calls,[])
    def test_handler_not_callable(self):
        with self.assertRaises(AgentDispatchDenied): dispatch_paper_agent('finance.agent',None,handlers={'finance.agent':None},certified_ids=frozenset({'finance.agent'}))
