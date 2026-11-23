"""Regression for TypeError fallback: a failed run must never be retried without payload."""
import ast
import pathlib
import types
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET = ROOT / "app" / "runtime" / "mind_trader_institutional_wiring.py"

class RunDispatchSafetyTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(TARGET.read_text(encoding="utf-8"))
        nodes = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
        nodes += [node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MODULES" for t in node.targets)]
        nodes += [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "run_institutional_wiring"]
        self.ns = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(TARGET), "exec"), self.ns)
        self.ns["MODULES"] = ["test.mock.module"]

    def test_internal_typeerror_never_retried(self):
        calls = []
        def run(payload):
            calls.append(payload)
            raise TypeError("internal failure")
        module = types.SimpleNamespace(run=run)
        with patch.object(self.ns["importlib"], "import_module", return_value=module):
            result = self.ns["run_institutional_wiring"]({"mode":"PAPER_ONLY"})
        self.assertEqual(len(calls), 1)
        self.assertFalse(result["results"][0]["run_ok"])
        self.assertIn("internal failure", result["results"][0]["error"])

    def test_parameterless_run_not_executed(self):
        calls = []
        def run():
            calls.append(True)
        module = types.SimpleNamespace(run=run)
        with patch.object(self.ns["importlib"], "import_module", return_value=module):
            result = self.ns["run_institutional_wiring"]({"mode":"PAPER_ONLY"})
        self.assertEqual(calls, [])
        self.assertFalse(result["results"][0]["run_ok"])
        self.assertIn("run_error=", result["results"][0]["error"])

if __name__ == "__main__":
    unittest.main()
