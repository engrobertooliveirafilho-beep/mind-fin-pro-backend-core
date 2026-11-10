import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.experimental.et665_r415_e2e_evidence_gate import verify

class E2EEvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.manifest={"hp19":[{"historical_id":f"HP{i}"} for i in range(19)]}
        self.evidence={"runs":[]}
        for i in range(19):
            for key,ext,data in (("input","json",'{"component":"real"}'),("output","json",'{"status":"ok","value":1}'),("log","log","processed")):
                path=self.root/f"{i}_{key}.{ext}"
                path.write_text(data)
            import hashlib
            run={"historical_id":f"HP{i}","mode":"PAPER","real_orders":False,"status":"PASS",
                 "result_type":"processed","source_sha256":"a"*64,"component_sha256":"b"*64}
            for key,ext in (("input","json"),("output","json"),("log","log")):
                path=self.root/f"{i}_{key}.{ext}"
                run[key]=path.name
                run[key+"_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
            self.evidence["runs"].append(run)
    def test_complete_evidence_only_ready_for_review(self):
        result=verify(self.root,self.manifest,self.evidence)
        self.assertEqual(result["status"],"READY_FOR_INDEPENDENT_REVIEW")
        self.assertFalse(result["verified_e2e"])
    def test_missing_motor_rejected(self):
        self.evidence["runs"].pop()
        self.assertEqual(verify(self.root,self.manifest,self.evidence)["status"],"BLOCKED")
    def test_tampered_output_rejected(self):
        (self.root/"0_output.json").write_text('{"status":"error"}')
        self.assertIn("ARTIFACT_HASH_MISMATCH",verify(self.root,self.manifest,self.evidence)["errors"])
    def test_real_orders_rejected(self):
        self.evidence["runs"][0]["real_orders"]=True
        self.assertIn("UNSAFE_MODE",verify(self.root,self.manifest,self.evidence)["errors"])
    def test_reused_output_rejected(self):
        self.evidence["runs"][1]["output"]=self.evidence["runs"][0]["output"]
        self.evidence["runs"][1]["output_sha256"]=self.evidence["runs"][0]["output_sha256"]
        self.assertIn("REUSED_EVIDENCE",verify(self.root,self.manifest,self.evidence)["errors"])
if __name__=="__main__":
    unittest.main()
