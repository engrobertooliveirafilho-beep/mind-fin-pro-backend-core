import hashlib,unittest
from r850_verified_dispatch import dispatch_verified
B=b'recovered source'; H=hashlib.sha256(B).hexdigest()
S={'id':10,'title':'memory','approved':True,'source_sha256':H}
def go(payload=None,sources=None,trusted=None,agent='dev.step_planner_agent'):
 return dispatch_verified(agent,{'approved_steps':[S]} if payload is None else payload,{10:B} if sources is None else sources,{10:H} if trusted is None else trusted)
class Tests(unittest.TestCase):
 def test_ok(self):self.assertEqual(go()['status'],'planned')
 def test_attested(self):self.assertTrue(go()['source_attested'])
 def test_not_certified(self):self.assertFalse(go()['runtime_certified'])
 def test_not_integrated(self):self.assertFalse(go()['integration_authorized'])
 def test_stub(self):self.assertEqual(go(agent='dev.code_blueprint_agent')['status'],'blocked')
 def test_unknown(self):self.assertEqual(go(agent='other')['status'],'blocked')
 def test_bad_agent(self):self.assertEqual(go(agent=[])['status'],'blocked')
 def test_bad_payload(self):self.assertEqual(go(payload=[])['status'],'blocked')
 def test_missing_source(self):self.assertEqual(go(sources={})['status'],'blocked')
 def test_modified_source(self):self.assertEqual(go(sources={10:b'changed'})['status'],'blocked')
 def test_wrong_trust(self):self.assertEqual(go(trusted={10:'f'*64})['status'],'blocked')
 def test_wrong_claim(self):self.assertEqual(go(payload={'approved_steps':[dict(S,source_sha256='f'*64)]})['status'],'blocked')
 def test_unapproved(self):self.assertEqual(go(payload={'approved_steps':[dict(S,approved=False)]})['status'],'blocked')
 def test_duplicate(self):self.assertEqual(go(payload={'approved_steps':[S,S]})['status'],'blocked')
 def test_unhashable(self):self.assertEqual(go(payload={'approved_steps':[dict(S,id=[])]})['status'],'blocked')
 def test_extra_source(self):self.assertEqual(go(sources={10:B,11:B})['status'],'blocked')
if __name__=='__main__':unittest.main()
