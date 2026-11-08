import hashlib
import tempfile
import unittest
from pathlib import Path
from mind_trader.security.et665_r65_authority_gate import ROLES, assess

class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.commit='a'*40
        self.evidence={}
        self.trust={'git_commit':self.commit,'sha256_by_role':{}}
        for role in ROLES:
            p=self.root/(role+'.txt')
            p.write_text(role)
            self.evidence[role]={'path':p.name,'git_commit':self.commit}
            self.trust['sha256_by_role'][role]=hashlib.sha256(p.read_bytes()).hexdigest()
    def tearDown(self):self.tmp.cleanup()
    def test_complete_still_not_certified(self):
        r=assess(self.evidence,self.trust,self.root)
        self.assertTrue(r['integrity_complete'])
        self.assertFalse(r['phase_b_certified'])
        self.assertFalse(r['authority_certified'])
    def test_no_trust_root(self):
        del self.trust['sha256_by_role']['isolation_p79']
        self.assertFalse(assess(self.evidence,self.trust,self.root)['integrity_complete'])
    def test_reused_file(self):
        self.evidence['isolation_p79']=dict(self.evidence['isolation_p77'])
        self.trust['sha256_by_role']['isolation_p79']=self.trust['sha256_by_role']['isolation_p77']
        self.assertEqual(assess(self.evidence,self.trust,self.root)['checks']['isolation_p79'],'REUSED_EVIDENCE')
    def test_wrong_commit(self):
        self.evidence['git_inventory']['git_commit']='b'*40
        self.assertEqual(assess(self.evidence,self.trust,self.root)['checks']['git_inventory'],'COMMIT_NOT_PINNED')
    def test_bad_hash(self):
        self.trust['sha256_by_role']['reconciliation']='0'*64
        self.assertEqual(assess(self.evidence,self.trust,self.root)['checks']['reconciliation'],'HASH_MISMATCH')
    def test_traversal(self):
        self.evidence['regression_junit']['path']='../../outside'
        self.assertEqual(assess(self.evidence,self.trust,self.root)['checks']['regression_junit'],'MISSING_OR_UNSAFE_PATH')
    def test_orders_blocked(self):
        r=assess(self.evidence,self.trust,self.root)
        self.assertEqual(r['real_orders'],'FORBIDDEN')
        self.assertEqual(r['ftmo_real'],'FORBIDDEN')
