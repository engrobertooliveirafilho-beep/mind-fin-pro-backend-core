"""Inventory-only modules must be reported as not wired, not silently ignored."""
import ast
import pathlib
import types
import unittest
from unittest.mock import patch

TARGET = pathlib.Path(__file__).resolve().parents[1] / "app" / "runtime" / "mind_trader_institutional_wiring.py"

class NoEntrypointTests(unittest.TestCase):
    def test_empty_registry_fails_closed(self):
        tree = ast.parse(TARGET.read_text(encoding="utf-8"))
        nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        nodes += [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MODULES" for t in n.targets)]
        nodes += [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_institutional_wiring"]
        ns = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(TARGET), "exec"), ns)
        ns["MODULES"] = []
        result = ns["run_institutional_wiring"]({"mode": "PAPER_ONLY"})
        self.assertEqual(result["status"], "DEGRADED")
        self.assertEqual(result["modules_total"], 0)

    def test_missing_run_classified_without_executing_anything(self):
        tree = ast.parse(TARGET.read_text(encoding="utf-8"))
        nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        nodes += [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MODULES" for t in n.targets)]
        nodes += [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_institutional_wiring"]
        ns = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(TARGET), "exec"), ns)
        ns["MODULES"] = ["app.runtime.p2071_2080_realtime_paper_runtime"]
        with patch.object(ns["importlib"], "import_module", return_value=types.SimpleNamespace(run_p2071_2080=lambda **kw: (_ for _ in ()).throw(AssertionError("must not execute")))):
            result = ns["run_institutional_wiring"]({"mode":"PAPER_ONLY"})
        self.assertEqual(result["status"], "DEGRADED")
        self.assertEqual(result["runs_ok"], 0)
        self.assertIn("NO_SUPPORTED_ENTRYPOINT", result["results"][0]["error"])

if __name__ == "__main__":
    unittest.main()
