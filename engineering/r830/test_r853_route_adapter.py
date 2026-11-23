import unittest
from r853_route_adapter import route_dry
A='dev.step_planner_agent'
def ok(a,p):return {'status':'planned','plan':[1],'integration_authorized':False,'runtime_certified':False}
class Tests(unittest.TestCase):
 def test_valid(self):self.assertEqual(route_dry(A,{},ok)['status'],'planned')
 def test_plan(self):self.assertEqual(route_dry(A,{},ok)['plan'],[1])
 def test_agent(self):self.assertEqual(route_dry(A,{},ok)['agent_id'],A)
 def test_none_payload(self):self.assertEqual(route_dry(A,None,ok)['status'],'planned')
 def test_bad_id(self):self.assertEqual(route_dry('',{},ok)['status'],'blocked')
 def test_bad_id_type(self):self.assertEqual(route_dry([],{},ok)['status'],'blocked')
 def test_path_injection(self):self.assertEqual(route_dry('../x',{},ok)['status'],'blocked')
 def test_bad_payload(self):self.assertEqual(route_dry(A,[],ok)['status'],'blocked')
 def test_no_dispatch(self):self.assertEqual(route_dry(A,{},None)['status'],'blocked')
 def test_offline(self):self.assertEqual(route_dry(A,{},ok,dry_run=False)['status'],'blocked')
 def test_bad_result(self):self.assertEqual(route_dry(A,{},lambda a,p:None)['status'],'blocked')
 def test_stub(self):self.assertEqual(route_dry(A,{},lambda a,p:{'status':'not_implemented'})['status'],'blocked')
 def test_no_evidence(self):self.assertEqual(route_dry(A,{},lambda a,p:{'status':'planned'})['status'],'blocked')
 def test_runtime_true(self):self.assertEqual(route_dry(A,{},lambda a,p:dict(ok(a,p),runtime_certified=True))['status'],'blocked')
 def test_integration_true(self):self.assertEqual(route_dry(A,{},lambda a,p:dict(ok(a,p),integration_authorized=True))['status'],'blocked')
 def test_exception(self):
  def fail(a,p):raise RuntimeError('secret')
  self.assertEqual(route_dry(A,{},fail)['reason'],'dispatch_failed')
if __name__=='__main__':unittest.main()
