import tempfile
import unittest
from pathlib import Path
from mind_trader.experimental.et665_r411_source_classifier import classify

class SourceClassifierTests(unittest.TestCase):
    def test_candidates_dispatcher_and_nonexecutors(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            agents=root/"app"/"agents"
            agents.mkdir(parents=True)
            (agents/"actual.py").write_text("def run_dry(payload):\n    return {'ok': True}\n")
            (agents/"other.py").write_text("def helper():\n    return 1\n")
            meta=root/"app"/"meta"
            meta.mkdir()
            (meta/"agents_unified_runtime.py").write_text(
                "from app.agents.actual import run_dry\nfrom app.agents.other import run_dry\n")
            report=classify(root)
            self.assertEqual(report["candidate_count"],1)
            self.assertEqual(report["functional_certified"],0)
            self.assertEqual(len(report["files"]),3)
            self.assertTrue(any(f.get("warning")=="DUPLICATE_RUN_DRY_IMPORT" for f in report["files"]))
    def test_invalid_source_not_certified(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            agents=root/"app"/"agents"
            agents.mkdir(parents=True)
            (agents/"broken.py").write_text("def run_dry(\n")
            report=classify(root)
            self.assertEqual(report["candidate_count"],0)
            self.assertEqual(report["files"][0]["kind"],"INVALID_SOURCE")
            self.assertEqual(report["functional_certified"],0)
if __name__=="__main__":
    unittest.main()
