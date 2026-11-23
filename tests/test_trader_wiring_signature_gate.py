"""P2224 run(cycles=30) must not receive the orchestration payload as cycles."""
import ast
import pathlib
import types
import unittest
from unittest.mock import patch

TARGET = pathlib.Path(__file__).resolve().parents[1] / "app" / "runtime" / "mind_trader_institutional_wiring.py"

class SignatureGateTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(TARGET.read_text(encoding="utf-8"))
        nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        nodes += [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MODULES" for t in n.targets)]
        nodes += [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_institutional_wiring"]
        self.ns = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(TARGET), "exec"), self.ns)
        self.ns["MODULES"] = ["app.runtime.p2224_2226_institutional_core"]

    def test_cycles_signature_rejected_without_execution(self):
        calls = []
        def run(cycles=30):
            calls.append(cycles)
            return {"status":"PASS"}
        with patch.object(self.ns["importlib"], "import_module", return_value=types.SimpleNamespace(run=run)):
            result = self.ns["run_institutional_wiring"]({"mode":"PAPER_ONLY"})
        self.assertEqual(calls, [])
        self.assertEqual(result["status"], "DEGRADED")
        self.assertIn("UNSUPPORTED_RUN_SIGNATURE", result["results"][0]["error"])

    def test_failed_status_never_counts_as_run_success(self):
        for status in ("FAIL", "FAILED", "ERROR", "BLOCKED", "DEGRADED", "NOT_CERTIFIED"):
            with self.subTest(status=status):
                def run(payload):
                    return {"status": status}
                with patch.object(self.ns["importlib"], "import_module", return_value=types.SimpleNamespace(run=run)):
                    result = self.ns["run_institutional_wiring"]({"mode":"PAPER_ONLY"})
                self.assertEqual(result["runs_ok"], 0)
                self.assertEqual(result["status"], "DEGRADED")

    def test_payload_signature_accepted(self):
        calls = []
        def run(payload):
            calls.append(payload)
            return {"status":"PAPER_ONLY"}
        with patch.object(self.ns["importlib"], "import_module", return_value=types.SimpleNamespace(run=run)):
            result = self.ns["run_institutional_wiring"]({"mode":"PAPER_ONLY"})
        self.assertEqual(calls, [{"mode":"PAPER_ONLY"}])
        self.assertEqual(result["status"], "PAPER_RUN_COMPLETED_UNCERTIFIED")

if __name__ == "__main__":
    unittest.main()
