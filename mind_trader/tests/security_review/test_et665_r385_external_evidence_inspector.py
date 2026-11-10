import tempfile,unittest,hashlib
from pathlib import Path
from mind_trader.experimental.et665_r385_external_evidence_inspector import inspect
from mind_trader.experimental.et665_r365_phase_b_evidence_gate import FRONTS
class R385(unittest.TestCase):
    def test_empty_manifest_blocks_all(self):
        with tempfile.TemporaryDirectory() as d:
            r=inspect(d,{"schema":"ET665.R365.v1","fronts":{}})
        self.assertEqual(r["evidence_records_passing_schema_hash_and_flag"],0)
        self.assertEqual(len(r["evidence_fronts"]),16)
        self.assertEqual(r["official_hp19_certified"],0)
    def test_tampered_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"evidence.txt";p.write_text("original")
            front=FRONTS[0]
            record={"front_id":front,"status":"PASS","artifact_sha256":hashlib.sha256(b"original").hexdigest(),"artifact_path":"evidence.txt","test_command":"offline-test","exit_code":0,"commit_sha":"abcdef012345","reviewer_approval":True}
            p.write_text("tampered")
            r=inspect(d,{"schema":"ET665.R365.v1","fronts":{front:record}})
        self.assertEqual(r["evidence_fronts"][front],"BLOCKED")
        self.assertEqual(r["phase_b_independently_certified"],0)
    def test_self_declared_review_does_not_certify(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"evidence.txt";p.write_text("original")
            front=FRONTS[0]
            record={"front_id":front,"status":"PASS","artifact_sha256":hashlib.sha256(b"original").hexdigest(),"artifact_path":"evidence.txt","test_command":"offline-test","exit_code":0,"commit_sha":"abcdef012345","reviewer_approval":True}
            r=inspect(d,{"schema":"ET665.R365.v1","fronts":{front:record}})
        self.assertEqual(r["evidence_records_passing_schema_hash_and_flag"],1)
        self.assertFalse(r["external_review_independently_authenticated"])
        self.assertEqual(r["phase_b_independently_certified"],0)
    def test_unknown_front_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):inspect(d,{"schema":"ET665.R365.v1","fronts":{"fake":{}}})
if __name__=="__main__":unittest.main()
