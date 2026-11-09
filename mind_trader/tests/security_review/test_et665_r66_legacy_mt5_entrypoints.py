"""ET665 R66: ensure legacy MT5 entrypoints remain inert, offline."""
import ast
import runpy
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
TARGETS = {
    "P77": ROOT / "reports/P77_DEMO_ORDER_CHECK_ONLY/p77_order_check_only.py",
    "P77B": ROOT / "reports/P77B_DEMO_ORDER_CHECK_FILLING_MODE_FIX/p77b_filling_check.py",
    "P79": ROOT / "reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_monitor.py",
}
BLOCK = "ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"

class HistoricalMT5IsolationTests(unittest.TestCase):
    def test_static_no_mt5_import_or_terminal_call(self):
        for name, path in TARGETS.items():
            with self.subTest(name=name):
                tree=ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node,ast.Import):
                        self.assertFalse(any(x.name.startswith("MetaTrader5") for x in node.names))
                    if isinstance(node,ast.ImportFrom):
                        self.assertFalse((node.module or "").startswith("MetaTrader5"))
                    if isinstance(node,ast.Call):
                        self.assertFalse(isinstance(node.func,ast.Attribute) and node.func.attr in {"initialize","order_send","order_check","positions_get"})

    def test_direct_function_call_denied(self):
        for name,path in TARGETS.items():
            with self.subTest(name=name):
                namespace=runpy.run_path(str(path),run_name="__test__")
                fn=namespace["check" if name=="P77B" else "run"]
                with self.assertRaisesRegex(PermissionError,BLOCK):
                    fn()

    def test_main_entrypoint_denied_without_mt5_import(self):
        import builtins
        real_import=builtins.__import__
        def guard(name,*args,**kwargs):
            if name.startswith("MetaTrader5"):
                raise AssertionError("MT5_IMPORT_ATTEMPT")
            return real_import(name,*args,**kwargs)
        for name,path in TARGETS.items():
            with self.subTest(name=name),patch("builtins.__import__",side_effect=guard):
                with self.assertRaisesRegex(PermissionError,BLOCK):
                    runpy.run_path(str(path),run_name="__main__")

if __name__=="__main__":
    unittest.main()
