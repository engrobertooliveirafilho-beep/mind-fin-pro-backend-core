"""A child health hook must never be invoked during PAPER orchestration."""
import ast
import pathlib
import types
import unittest
from unittest.mock import patch

TARGET = pathlib.Path(__file__).resolve().parents[1] / "app" / "runtime" / "mind_trader_institutional_wiring.py"

class ChildHealthSafetyTests(unittest.TestCase):
    def test_child_health_is_not_executed(self):
        tree = ast.parse(TARGET.read_text(encoding="utf-8"))
        nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        nodes += [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MODULES" for t in n.targets)]
        nodes += [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_institutional_wiring"]
        ns = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(TARGET), "exec"), ns)
        ns["MODULES"] = ["test.mock.module"]
        calls = []
        def dangerous_health():
            calls.append("health")
            raise AssertionError("health must never execute")
        module = types.SimpleNamespace(health=dangerous_health, run=lambda payload: {"mode":payload["mode"]})
        with patch.object(ns["importlib"], "import_module", return_value=module):
            result = ns["run_institutional_wiring"]({"mode":"PAPER_ONLY"})
        self.assertEqual(calls, [])
        self.assertEqual(result["results"][0]["health_inspection"], "SKIPPED_SIDE_EFFECT_SAFETY")
        self.assertEqual(result["status"], "PAPER_RUN_COMPLETED_UNCERTIFIED")
        self.assertEqual(result["health_ok"], 0)

if __name__ == "__main__":
    unittest.main()
