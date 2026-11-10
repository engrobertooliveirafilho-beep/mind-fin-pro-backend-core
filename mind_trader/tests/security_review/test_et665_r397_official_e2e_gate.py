import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.experimental.et665_r396_official_e2e_gate import verify

class R397Gate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.root.joinpath("component.py").write_text("def run(x): return x + 1\n")
        self.root.joinpath("input.json").write_text('{"x":1}')
        self.root.joinpath("output.json").write_text('{"y":2}')
        self.root.joinpath("execution.log").write_text("run: PASS")
        def rec(name):
            return {"path": name, "sha256": hashlib.sha256((self.root/name).read_bytes()).hexdigest()}
        def entry(prefix, n):
            return {"historical_id": f"{prefix}-{n}", "status":"PASS", "mode":"PAPER",
                    "synthetic":False, "independent_review":True, "reviewer":"external-reviewer",
                    "source":rec("component.py"),"input":rec("input.json"),
                    "output":rec("output.json"),"execution_log":rec("execution.log")}
        self.manifest={"hp19":[entry("HP",i) for i in range(19)],
                       "phase_b":[entry("B",i) for i in range(16)]}

    def test_complete_evidence_only_ready_for_review(self):
        result=verify(self.root,self.manifest)
        self.assertEqual(result["status"],"EVIDENCE_READY_FOR_HUMAN_REVIEW")
        self.assertEqual((result["hp19"],result["phase_b"]),(19,16))
        self.assertIn("No automatic",result["note"])

    def test_missing_motor_fails(self):
        self.manifest["hp19"].pop()
        self.assertEqual(verify(self.root,self.manifest)["status"],"FAIL_CLOSED")

    def test_duplicate_historical_id_fails(self):
        self.manifest["hp19"][1]["historical_id"]=self.manifest["hp19"][0]["historical_id"]
        self.assertEqual(verify(self.root,self.manifest)["status"],"FAIL_CLOSED")

    def test_synthetic_fails(self):
        self.manifest["hp19"][0]["synthetic"]=True
        self.assertEqual(verify(self.root,self.manifest)["status"],"FAIL_CLOSED")

    def test_tampered_output_fails(self):
        (self.root/"output.json").write_text('{"y":999}')
        self.assertEqual(verify(self.root,self.manifest)["status"],"FAIL_CLOSED")

    def test_missing_review_fails(self):
        self.manifest["phase_b"][0]["independent_review"]=False
        self.assertEqual(verify(self.root,self.manifest)["status"],"FAIL_CLOSED")

    def test_path_traversal_fails(self):
        self.manifest["hp19"][0]["source"]["path"]="../outside.py"
        self.assertEqual(verify(self.root,self.manifest)["status"],"FAIL_CLOSED")

    def test_symlink_fails(self):
        link=self.root/"link.py"
        try:
            link.symlink_to(self.root/"component.py")
        except (OSError,NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.manifest["hp19"][0]["source"]["path"]="link.py"
        self.assertEqual(verify(self.root,self.manifest)["status"],"FAIL_CLOSED")

if __name__=="__main__":
    unittest.main()
