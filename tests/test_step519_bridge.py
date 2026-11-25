import unittest
from app.meta.step519_bridge import execute_plan

class Metrics:
    def record_agent_turn(self, profile): pass

class BridgeTests(unittest.TestCase):
    def run_plan(self, registry, mapping=None):
        plan = {'steps': [{'step_index': i, 'assigned_agent_role': role, 'description': role} for i, role in enumerate(('risk','execution'))]}
        return execute_plan(plan, role_map={'risk':'a','execution':'b'} if mapping is None else mapping, registry=registry, metrics=Metrics(), profile='test')
    def test_success(self):
        self.assertEqual(self.run_plan({'a':lambda p:{'agent_id':'a','status':'ok'},'b':lambda p:{'agent_id':'b','status':'ok'}})['status'],'completed')
    def test_missing_preflight(self):
        calls=[]
        self.assertEqual(self.run_plan({'a':lambda p:calls.append(p)})['status'],'blocked')
        self.assertEqual(calls,[])
    def test_stub_stops(self):
        calls=[]
        r=self.run_plan({'a':lambda p:{'agent_id':'a','status':'ok','mode':'stub'},'b':lambda p:calls.append(p)})
        self.assertEqual(r['status'],'blocked'); self.assertEqual(calls,[])
    def test_identity_mismatch(self):
        r=self.run_plan({'a':lambda p:{'agent_id':'wrong','status':'ok'},'b':lambda p:None})
        self.assertEqual(r['status'],'blocked'); self.assertEqual(len(r['results']),1)
