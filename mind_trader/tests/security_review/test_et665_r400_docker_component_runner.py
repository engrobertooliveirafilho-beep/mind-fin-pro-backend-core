import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from mind_trader.experimental.et665_r400_docker_component_runner import run

class DockerComponentGate(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/"component.py").write_text("import sys\nprint(sys.stdin.read())\n")
        (self.root/"input.json").write_text('{"real":true}')
        def sha(p): return hashlib.sha256((self.root/p).read_bytes()).hexdigest()
        self.data={"components":[{"historical_id":"HP19-01","component":"component.py",
                  "sha256":sha("component.py"),"input":"input.json",
                  "input_sha256":sha("input.json")}]}
        self.manifest=self.root/"manifest.json"
        self.output=self.root/"evidence"
        self.save()
    def save(self): self.manifest.write_text(json.dumps(self.data))
    def test_missing_docker_fails_closed(self):
        with patch("subprocess.run",side_effect=FileNotFoundError()):
            result=run(self.root,self.manifest,self.output)
        self.assertEqual(result["status"],"FAIL_CLOSED")
        self.assertTrue((self.output/"r400_report.json").is_file())
    def test_hash_tamper_rejected(self):
        (self.root/"component.py").write_text("print('changed')")
        with patch("subprocess.run") as mocked:
            result=run(self.root,self.manifest,self.output)
        mocked.assert_not_called()
        self.assertEqual(result["status"],"FAIL_CLOSED")
    def test_success_not_certification(self):
        class Completed:
            returncode=0
            stdout=b'{"real":true}\n'
            stderr=b''
        with patch("subprocess.run",return_value=Completed()) as mocked:
            result=run(self.root,self.manifest,self.output)
        self.assertEqual(result["status"],"EXECUTED_UNCERTIFIED")
        self.assertEqual(result["official_hp19_certified"],0)
        self.assertEqual(result["phase_b_certified"],0)
        command=mocked.call_args.args[0]
        self.assertIn("--network",command)
        self.assertIn("none",command)
        self.assertIn("--read-only",command)
        self.assertIn("--cap-drop",command)
        self.assertEqual((self.output/"run_00.stdout").read_bytes(),Completed.stdout)
    def test_duplicate_id_rejected(self):
        self.data["components"].append(dict(self.data["components"][0]))
        self.save()
        with patch("subprocess.run") as mocked:
            result=run(self.root,self.manifest,self.output)
        self.assertEqual(result["status"],"FAIL_CLOSED")
    def test_outside_path_rejected(self):
        self.data["components"][0]["component"]="../outside.py"
        self.save()
        with patch("subprocess.run") as mocked:
            result=run(self.root,self.manifest,self.output)
        mocked.assert_not_called()
        self.assertEqual(result["status"],"FAIL_CLOSED")

if __name__=="__main__":unittest.main()
