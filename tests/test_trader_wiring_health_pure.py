"""Regression: health must not import, execute, or claim runtime certification."""
import ast
import pathlib
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET = ROOT / "app" / "runtime" / "mind_trader_institutional_wiring.py"

class HealthIsolationTests(unittest.TestCase):
    def setUp(self):
        source = TARGET.read_text(encoding="utf-8")
        tree = ast.parse(source)
        modules = next(node.value for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MODULES" for t in node.targets))
        health = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "health")
        self.namespace = {"MODULES": ast.literal_eval(modules)}
        exec(compile(ast.Module(body=[health], type_ignores=[]), str(TARGET), "exec"), self.namespace)

    def test_health_never_runs_modules(self):
        with patch("builtins.__import__", side_effect=AssertionError("unexpected import")):
            result = self.namespace["health"]()
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertTrue(result["inspection_only"])

    def test_health_does_not_invent_success_counts(self):
        result = self.namespace["health"]()
        self.assertEqual(result["modules_total"], 10)
        for key in ("imports_ok", "runs_ok", "health_ok"):
            self.assertIsNone(result[key])

if __name__ == "__main__":
    unittest.main()
