"""ET665.R67: source-only fail-closed checks. Never import trader modules or connect MT5."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
TARGETS = {
    "mind_trader/reports/P77_DEMO_ORDER_CHECK_ONLY/p77_order_check_only.py": ("run", "ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"),
    "mind_trader/reports/P77B_DEMO_ORDER_CHECK_FILLING_MODE_FIX/p77b_filling_check.py": ("check", "ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"),
    "mind_trader/reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_monitor.py": ("run", "ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"),
    "mind_trader/reports/P1505_DATA_INGESTION_ENGINE/p1505b_mt5_harvester.py": ("run", "ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"),
    "mind_trader/app/p86_execution_intelligence_domain/engine.py": ("mt5_snapshot", "ET665_BJ_MT5_CONNECTIVITY_DISABLED_PENDING_SECURITY_REVIEW"),
    "mind_trader/app/p1621e_real_video_fetch_loop/engine.py": ("fetch_metadata", "ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW"),
    "mind_trader/app/p1622_autonomous_daily_research_cron/engine.py": ("run_module", "ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW"),
}

class TestR67ResidualRoutes(unittest.TestCase):
    def test_direct_guards_are_first_statement(self):
        for relative, (name, marker) in TARGETS.items():
            with self.subTest(path=relative, function=name):
                tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
                methods = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
                self.assertEqual(len(methods), 1)
                body = methods[0].body
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    body = body[1:]
                self.assertTrue(body, "guarded function body must not be empty")
                first = body[0]
                self.assertIsInstance(first, ast.Raise)
                self.assertIsInstance(first.exc, ast.Call)
                self.assertIsInstance(first.exc.func, ast.Name)
                self.assertIn(first.exc.func.id, {"PermissionError", "RuntimeError"})
                self.assertTrue(first.exc.args)
                self.assertIsInstance(first.exc.args[0], ast.Constant)
                self.assertEqual(first.exc.args[0].value, marker)

    def test_high_risk_modules_have_guarded_run(self):
        for relative in (
            "mind_trader/app/p1621e_real_video_fetch_loop/engine.py",
            "mind_trader/app/p1622_autonomous_daily_research_cron/engine.py",
        ):
            with self.subTest(path=relative):
                tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
                run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
                first = run.body[0]
                self.assertIsInstance(first, ast.Raise)
                self.assertIn("ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW", ast.unparse(first))

    def test_no_source_execution(self):
        # The suite intentionally parses source only. No importlib, exec, subprocess or socket.
        text = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(text)
        imports = {alias.name for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom)) for alias in n.names}
        self.assertFalse(imports & {"MetaTrader5", "subprocess", "socket", "importlib"})

if __name__ == "__main__":
    unittest.main()
