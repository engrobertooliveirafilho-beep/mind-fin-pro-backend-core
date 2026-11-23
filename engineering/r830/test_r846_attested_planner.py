import hashlib
import unittest
from r846_attested_planner import plan_attested

B=b'original source code bytes'
H=hashlib.sha256(B).hexdigest()
S={'id':10,'title':'STEP 10','approved':True,'source_sha256':H}

def go(steps=None, blobs=None, digests=None):
    return plan_attested({'approved_steps':[S] if steps is None else steps}, {10:B} if blobs is None else blobs, {10:H} if digests is None else digests)

class TestAttestation(unittest.TestCase):
    def test_valid(self):self.assertEqual(go()['status'],'planned')
    def test_attested(self):self.assertTrue(go()['source_attested'])
    def test_not_runtime(self):self.assertFalse(go()['runtime_certified'])
    def test_not_integrated(self):self.assertFalse(go()['integration_authorized'])
    def test_wrong_bytes(self):self.assertEqual(go(blobs={10:b'changed'})['reason'],'digest_mismatch')
    def test_wrong_trust(self):self.assertEqual(go(digests={10:'0'*64})['reason'],'digest_mismatch')
    def test_wrong_claim(self):self.assertEqual(go(steps=[dict(S,source_sha256='f'*64)])['reason'],'digest_mismatch')
    def test_none_bytes(self):self.assertEqual(go(blobs={10:None})['reason'],'invalid_evidence')
    def test_none_digest(self):self.assertEqual(go(digests={10:None})['reason'],'invalid_evidence')
    def test_upper_digest(self):self.assertEqual(go(digests={10:H.upper()})['reason'],'invalid_evidence')
    def test_extra_source(self):self.assertEqual(go(blobs={10:B,11:B})['reason'],'source_set_mismatch')
    def test_missing_source(self):self.assertEqual(go(blobs={})['reason'],'source_set_mismatch')
    def test_extra_trust(self):self.assertEqual(go(digests={10:H,11:H})['reason'],'source_set_mismatch')
    def test_empty(self):self.assertEqual(go(steps=[])['reason'],'invalid_batch')
    def test_non_dict(self):self.assertEqual(plan_attested(None,{}, {})['reason'],'invalid_inputs')
    def test_bad_step(self):self.assertEqual(go(steps=['x'])['status'],'blocked')
    def test_unapproved(self):self.assertEqual(go(steps=[dict(S,approved=False)])['status'],'blocked')
    def test_duplicate(self):self.assertEqual(go(steps=[S,S])['status'],'blocked')
    def test_extra_field(self):self.assertEqual(go(steps=[dict(S,extra='x')])['status'],'blocked')
    def test_no_exec(self):self.assertEqual(go()['plans'][0]['status'],'PLAN_ONLY')
if __name__=='__main__':unittest.main()
