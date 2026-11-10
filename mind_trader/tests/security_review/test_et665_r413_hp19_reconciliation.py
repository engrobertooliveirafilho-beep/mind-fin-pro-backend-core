import hashlib
import tempfile
import unittest
from pathlib import Path
from mind_trader.experimental.et665_r413_hp19_reconciliation import reconcile

class HP19ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.records=[]
        self.items=[]
        for i in range(19):
            p=f"app/agents/agent_{i}.py"
            target=self.root/p
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text("def run_dry(payload):\n    return payload\n")
            digest=hashlib.sha256(target.read_bytes()).hexdigest()
            self.records.append({"path":p,"kind":"HISTORICAL_CANDIDATE","sha256":digest})
            self.items.append({"historical_id":f"HP{i+1}","path":p,"sha256":digest})
    def check(self):
        return reconcile(self.root,{"files":self.records},{"hp19":self.items})
    def test_identity_only_never_functional_certification(self):
        r=self.check()
        self.assertTrue(r["identity_verified"])
        self.assertEqual(r["functional_certified"],0)
    def test_tampered_source_blocked(self):
        (self.root/self.items[0]["path"]).write_text("tampered")
        self.assertIn("SOURCE_HASH_MISMATCH",self.check()["errors"])
    def test_duplicate_id_blocked(self):
        self.items[1]["historical_id"]=self.items[0]["historical_id"]
        self.assertIn("INVALID_OR_DUPLICATE_ID",self.check()["errors"])
    def test_missing_source_blocked(self):
        (self.root/self.items[0]["path"]).unlink()
        self.assertIn("SOURCE_MISSING_OR_OUTSIDE",self.check()["errors"])
    def test_manifest_missing_entry_blocked(self):
        self.items.pop()
        self.assertIn("MANIFEST_MUST_HAVE_EXACTLY_19",self.check()["errors"])
    def test_path_traversal_blocked(self):
        self.items[0]["path"]="../escape.py"
        self.assertIn("UNSAFE_OR_DUPLICATE_PATH",self.check()["errors"])
if __name__=="__main__":
    unittest.main()
