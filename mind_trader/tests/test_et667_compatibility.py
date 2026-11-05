"""ET667: derived facade contract tests. No canonical runtime execution."""
import ast
import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "historical/derived/et667/mind_trader_institutional_wiring.py"

class ET667Compatibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("et667_derived_wiring", SOURCE)
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.mod
        spec.loader.exec_module(cls.mod)

    def test_factory_signature(self):
        self.assertTrue(callable(self.mod.create_paper_runtime))

    def test_fail_closed_status(self):
        h = self.mod.health()
        self.assertEqual(h["status"], "COMPATIBILITY_ONLY")
        self.assertFalse(h["historical_runtime_recovered"])

    def test_paper_only(self):
        self.assertEqual(self.mod.create_paper_runtime().mode, "PAPER_ONLY")

    def test_no_order_methods(self):
        obj = self.mod.create_paper_runtime()
        for name in ("connect", "run", "start", "send_order", "place_order", "submit_order"):
            self.assertFalse(callable(getattr(obj, name, None)))
        self.assertFalse(obj.order_execution)

    def test_no_network_imports(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        imports = {alias.name.split(".")[0] for node in ast.walk(tree)
                   if isinstance(node, ast.Import) for alias in node.names}
        self.assertFalse(imports & {"socket", "requests", "subprocess", "MetaTrader5"})

if __name__ == "__main__":
    unittest.main()
