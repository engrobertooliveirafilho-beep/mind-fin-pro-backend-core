import unittest
from agent_contract_v4 import validate_payload,certify_response,ContractRejected
class Tests(unittest.TestCase):
 def test_valid(self):self.assertTrue(validate_payload({'x':[1,2,'ok']}))
 def test_empty(self):self.assertTrue(validate_payload({}))
 def test_nested(self):self.assertTrue(validate_payload({'a':{'b':True}}))
 def test_bad_key(self):
  with self.assertRaises(ContractRejected):validate_payload({'REAL_ORDERS':False})
 def test_nested_key(self):
  with self.assertRaises(ContractRejected):validate_payload({'a':[{'place_order':0}]})
 def test_nonstring_key(self):
  with self.assertRaises(ContractRejected):validate_payload({1:2})
 def test_nan(self):
  with self.assertRaises(ContractRejected):validate_payload({'a':float('nan')})
 def test_inf(self):
  with self.assertRaises(ContractRejected):validate_payload({'a':float('inf')})
 def test_cycle(self):
  a={};a['x']=a
  with self.assertRaises(ContractRejected):validate_payload(a)
 def test_deep(self):
  a={};b=a
  for i in range(18):b['x']={};b=b['x']
  with self.assertRaises(ContractRejected):validate_payload(a)
 def test_object(self):
  with self.assertRaises(ContractRejected):validate_payload({'x':object()})
 def test_good_response_not_certified(self):self.assertFalse(certify_response('sec.sentinel',{'agent_id':'sec.sentinel','status':'ok','mode':'dry_run'})['functional_certified'])
 def test_stub(self):
  with self.assertRaises(ContractRejected):certify_response('sec.sentinel',{'agent_id':'sec.sentinel','status':'not_implemented','mode':'stub'})
 def test_mismatch(self):
  with self.assertRaises(ContractRejected):certify_response('sec.sentinel',{'agent_id':'sec.gatekeeper','status':'ok'})
 def test_live(self):
  with self.assertRaises(ContractRejected):certify_response('sec.sentinel',{'agent_id':'sec.sentinel','status':'ok','mode':'live'})
 def test_error(self):
  with self.assertRaises(ContractRejected):certify_response('sec.sentinel',{'agent_id':'sec.sentinel','status':'ok','error':'bad'})
 def test_missing_mode(self):
  with self.assertRaises(ContractRejected):certify_response('sec.sentinel',{'agent_id':'sec.sentinel','status':'ok'})
 def test_unknown_mode(self):
  with self.assertRaises(ContractRejected):certify_response('sec.sentinel',{'agent_id':'sec.sentinel','status':'ok','mode':'paper_live'})
 def test_broker_order(self):
  with self.assertRaises(ContractRejected):validate_payload({'broker_order':False})
 def test_submit_order_nested(self):
  with self.assertRaises(ContractRejected):validate_payload({'nested':{'submit_order':None}})
 def test_withdraw_funds(self):
  with self.assertRaises(ContractRejected):validate_payload({'withdraw_funds':0})
 def test_dry_run_response(self):
  self.assertTrue(certify_response('sec.sentinel',{'agent_id':'sec.sentinel','status':'ok','mode':'dry_run'})['contract_valid'])
if __name__=='__main__':unittest.main()
