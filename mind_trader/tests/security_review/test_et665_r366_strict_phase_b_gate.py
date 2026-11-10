"""ET665.R366 security regression: no false certification."""
import hashlib,tempfile,unittest
from pathlib import Path
from mind_trader.experimental.et665_r365_phase_b_evidence_gate import FRONTS
from mind_trader.experimental.et665_r366_strict_phase_b_gate import audit_strict
class R366(unittest.TestCase):
    def make(self,root,front,filename):
        data=b"test evidence";(root/filename).write_bytes(data)
        return {"front_id":front,"status":"PASS","artifact_sha256":hashlib.sha256(data).hexdigest(),
                "artifact_path":filename,"test_command":"python -m unittest",
                "exit_code":0,"commit_sha":"abcdef1234","reviewer_approval":True}
    def test_self_approval_never_certifies(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);record=self.make(root,FRONTS[0],"proof")
            result=audit_strict(root,{"schema":"ET665.R365.v1","fronts":{FRONTS[0]:record}})
            self.assertEqual(result["certified"],0)
            self.assertEqual(result["evidence_verified"],1)
            self.assertEqual(result["fronts"][FRONTS[0]],"PENDING_AUTHENTICATED_REVIEW")
    def test_reused_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);a=self.make(root,FRONTS[0],"a");b=self.make(root,FRONTS[1],"b")
            result=audit_strict(root,{"schema":"ET665.R365.v1","fronts":{FRONTS[0]:a,FRONTS[1]:b}})
            self.assertEqual(result["evidence_verified"],1)
            self.assertIn("reused evidence",result["fronts"][FRONTS[1]])
    def test_forged_review_injection_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"untrusted approval"):
                audit_strict(Path(d),{"schema":"ET665.R365.v1","fronts":{}},verified_approvals={FRONTS[0]:True})
    def test_missing_all_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            result=audit_strict(Path(d),{"schema":"ET665.R365.v1","fronts":{}})
            self.assertEqual(result["certified"],0)
            self.assertEqual(result["status"],"FAIL_CLOSED")
if __name__=="__main__":unittest.main()
