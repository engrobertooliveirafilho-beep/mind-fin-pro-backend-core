"""Regression for explicit PAPER_ONLY authorization and accurate aggregate status."""
import ast
import pathlib
import types
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET = ROOT / "app" / "runtime" / "mind_trader_institutional_wiring.py"

class PaperModeGateTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(TARGET.read_text(encoding="utf-8"))
        nodes = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
        nodes += [node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MODULES" for t in node.targets)]
        nodes += [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "run_institutional_wiring"]
        self.ns = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(TARGET), "exec"), self.ns)
        self.ns["MODULES"] = ["test.mock.module"]

    def test_rejects_unsafe_modes_before_import(self):
        for payload in (None, {}, {"mode":"LIVE"}, {"mode":"DEMO"}, {"mode":"PAPER_ONLY","real_orders":True}, {"mode":"PAPER_ONLY","ftmo_real":True}):
            with self.subTest(payload=payload):
                with patch.object(self.ns["importlib"], "import_module", side_effect=AssertionError("import must not occur")):
                    with self.assertRaises(ValueError):
                        self.ns["run_institutional_wiring"](payload)

    def test_failed_module_never_reports_operational(self):
        def run(payload):
            raise RuntimeError("simulated module failure")
        with patch.object(self.ns["importlib"], "import_module", return_value=types.SimpleNamespace(run=run)):
            result = self.ns["run_institutional_wiring"]({"mode":"PAPER_ONLY"})
        self.assertEqual(result["status"], "DEGRADED")
        self.assertEqual(result["runs_ok"], 0)

    def test_paper_only_success(self):
        with patch.object(self.ns["importlib"], "import_module", return_value=types.SimpleNamespace(run=lambda payload: {"mode":payload["mode"]})):
            result = self.ns["run_institutional_wiring"]({"mode":"PAPER_ONLY"})
        self.assertEqual(result["status"], "PAPER_RUN_COMPLETED_UNCERTIFIED")
        self.assertEqual(result["runs_ok"], 1)

if __name__ == "__main__":
    unittest.main()
