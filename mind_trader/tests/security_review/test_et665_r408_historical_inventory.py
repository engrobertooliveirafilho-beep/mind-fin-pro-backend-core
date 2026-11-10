import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.experimental.et665_r406_historical_inventory import inspect

class HistoricalInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.entries=[]
        for i in range(19):
            name=f"agent_{i:02d}.py"
            body=f"def run_dry(payload):\n    return {{'agent_id': {i}, 'payload': payload}}\n"
            (self.root/name).write_text(body,encoding="utf-8")
            self.entries.append({"historical_id":f"HP19-{i:02d}","path":name,
                 "sha256":hashlib.sha256((self.root/name).read_bytes()).hexdigest()})
        self.manifest=self.root/"inventory.json"
        self.save()
    def save(self):
        self.manifest.write_text(json.dumps({"hp19":self.entries}),encoding="utf-8")
    def test_19_sources_verified_but_not_certified(self):
        result=inspect(self.root,self.manifest)
        self.assertEqual(result["sources_sha256_verified"],19)
        self.assertEqual(result["functional_certified"],0)
        self.assertEqual(result["status"],"SOURCES_VERIFIED_FUNCTIONAL_PENDING")
    def test_duplicate_path_rejected(self):
        self.entries[1]["path"]=self.entries[0]["path"]
        self.entries[1]["sha256"]=self.entries[0]["sha256"]
        self.save()
        self.assertEqual(inspect(self.root,self.manifest)["status"],"FAIL_CLOSED")
    def test_tampered_source_rejected(self):
        (self.root/"agent_00.py").write_text("print('tampered')")
        self.assertEqual(inspect(self.root,self.manifest)["status"],"FAIL_CLOSED")
    def test_missing_source_rejected(self):
        (self.root/"agent_00.py").unlink()
        self.assertEqual(inspect(self.root,self.manifest)["status"],"FAIL_CLOSED")
    def test_syntax_error_rejected(self):
        bad=b"def broken(\n"
        (self.root/"agent_00.py").write_bytes(bad)
        self.entries[0]["sha256"]=hashlib.sha256(bad).hexdigest()
        self.save()
        self.assertEqual(inspect(self.root,self.manifest)["status"],"FAIL_CLOSED")

if __name__=="__main__":
    unittest.main()
