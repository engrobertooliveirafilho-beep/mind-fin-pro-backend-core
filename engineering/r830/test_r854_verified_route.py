import unittest,hashlib
from r854_verified_route import verified_route, AGENT
B=b'original fixture bytes'; H=hashlib.sha256(B).hexdigest()
S={'id':10,'title':'memory','approved':True,'source_sha256':H}
def run(payload=None,sources=None,trusted=None,agent=AGENT,dry_run=True):
 return verified_route(agent,{'approved_steps':[S]} if payload is None else payload,
                       {10:B} if sources is None else sources,
                       {10:H} if trusted is None else trusted,dry_run=dry_run)
class Tests(unittest.TestCase):
 def test_plan(self):self.assertEqual(run()['status'],'planned')
 def test_step(self):self.assertEqual(run()['plan'][0]['step_id'],10)
 def test_not_runtime(self):self.assertFalse(run()['runtime_certified'])
 def test_not_integrated(self):self.assertFalse(run()['integration_authorized'])
 def test_wrong_agent(self):self.assertEqual(run(agent='dev.code_blueprint_agent')['status'],'blocked')
 def test_unknown(self):self.assertEqual(run(agent='unknown.agent')['status'],'blocked')
 def test_bad_agent(self):self.assertEqual(run(agent=[])['status'],'blocked')
 def test_offline(self):self.assertEqual(run(dry_run=False)['status'],'blocked')
 def test_missing_source(self):self.assertEqual(run(sources={})['status'],'blocked')
 def test_missing_trust(self):self.assertEqual(run(trusted={})['status'],'blocked')
 def test_changed_bytes(self):self.assertEqual(run(sources={10:b'changed'})['status'],'blocked')
 def test_forged_trust(self):self.assertEqual(run(trusted={10:'f'*64})['status'],'blocked')
 def test_forged_claim(self):self.assertEqual(run(payload={'approved_steps':[dict(S,source_sha256='f'*64)]})['status'],'blocked')
 def test_unapproved(self):self.assertEqual(run(payload={'approved_steps':[dict(S,approved=False)]})['status'],'blocked')
 def test_duplicate(self):self.assertEqual(run(payload={'approved_steps':[S,S]})['status'],'blocked')
 def test_unhashable(self):self.assertEqual(run(payload={'approved_steps':[dict(S,id=[])]})['status'],'blocked')
 def test_bad_payload(self):self.assertEqual(run(payload=[])['status'],'blocked')
 def test_bad_title(self):self.assertEqual(run(payload={'approved_steps':[dict(S,title='')]})['status'],'blocked')
 def test_extra_source(self):self.assertEqual(run(sources={10:B,11:B})['status'],'blocked')
 def test_extra_field(self):self.assertEqual(run(payload={'approved_steps':[dict(S,extra=True)]})['status'],'blocked')
if __name__=='__main__':unittest.main()
