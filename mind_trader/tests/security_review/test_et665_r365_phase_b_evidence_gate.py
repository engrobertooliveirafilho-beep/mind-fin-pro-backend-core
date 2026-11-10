"""ET665.R365: evidence gate rejects empty, forged, traversed and partial proof."""
import hashlib,tempfile,unittest
from pathlib import Path
from mind_trader.experimental.et665_r365_phase_b_evidence_gate import FRONTS,audit

class R365Gate(unittest.TestCase):
    def test_empty_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit(Path(d),{"schema":"ET665.R365.v1","fronts":{}})
            self.assertEqual((r["verified"],r["total"],r["status"]),(0,16,"FAIL_CLOSED"))
    def test_single_front_does_not_certify(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"proof.txt").write_text("real test evidence")
            h=hashlib.sha256((root/"proof.txt").read_bytes()).hexdigest()
            record={"front_id":FRONTS[0],"status":"PASS","artifact_sha256":h,"artifact_path":"proof.txt",
                    "test_command":"python -m unittest","exit_code":0,"commit_sha":"abcdef123456","reviewer_approval":True}
            r=audit(root,{"schema":"ET665.R365.v1","fronts":{FRONTS[0]:record}})
            self.assertEqual(r["verified"],1)
            self.assertEqual(r["status"],"FAIL_CLOSED")
            record["artifact_sha256"]="0"*64
            self.assertEqual(audit(root,{"schema":"ET665.R365.v1","fronts":{FRONTS[0]:record}})["verified"],0)
    def test_traversal_and_unknown_front(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            record={"front_id":FRONTS[0],"status":"PASS","artifact_sha256":"0"*64,"artifact_path":"../escape",
                    "test_command":"test","exit_code":0,"commit_sha":"abcdef1","reviewer_approval":True}
            self.assertEqual(audit(root,{"schema":"ET665.R365.v1","fronts":{FRONTS[0]:record}})["verified"],0)
            with self.assertRaises(ValueError):
                audit(root,{"schema":"ET665.R365.v1","fronts":{"invented":record}})
    def test_no_auto_promotion(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit(Path(d),{"schema":"ET665.R365.v1","fronts":{}})
            self.assertFalse(r["promotion_authorized"])
            self.assertEqual(r["real_orders"],"FORBIDDEN")
if __name__=="__main__":unittest.main()
