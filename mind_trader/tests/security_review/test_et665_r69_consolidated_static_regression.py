"""R69: offline source-only regression, no trader imports, no network, no MT5."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
GUARDS = {
    "mind_trader/reports/P77_DEMO_ORDER_CHECK_ONLY/p77_order_check_only.py": ("run", "ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"),
    "mind_trader/reports/P77B_DEMO_ORDER_CHECK_FILLING_MODE_FIX/p77b_filling_check.py": ("check", "ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"),
    "mind_trader/reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_monitor.py": ("run", "ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"),
    "mind_trader/reports/P1505_DATA_INGESTION_ENGINE/p1505b_mt5_harvester.py": ("run", "ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED"),
    "mind_trader/app/p86_execution_intelligence_domain/engine.py": ("mt5_snapshot", "ET665_BJ_MT5_CONNECTIVITY_DISABLED_PENDING_SECURITY_REVIEW"),
    "mind_trader/app/p1621e_real_video_fetch_loop/engine.py": ("fetch_metadata", "ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW"),
    "mind_trader/app/p1621e_real_video_fetch_loop/engine.py#run": ("run", "ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW"),
    "mind_trader/app/p1622_autonomous_daily_research_cron/engine.py": ("run_module", "ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW"),
    "mind_trader/app/p1622_autonomous_daily_research_cron/engine.py#run": ("run", "ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW"),
}
GATEWAY = "products/eldora_trader/mind_trader/app/execution/gateway.py"
MERGER = "mind_trader/reports/P1505_DATA_INGESTION_ENGINE/p1505j_merge_diversified_mt5.py"

def source(relative):
    return (ROOT / relative.split("#")[0]).read_text(encoding="utf-8")

class R69StaticRegression(unittest.TestCase):
    def test_entrypoint_guards(self):
        for path, (name, marker) in GUARDS.items():
            with self.subTest(path=path):
                tree = ast.parse(source(path))
                functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
                self.assertEqual(len(functions), 1)
                first = functions[0].body[0]
                self.assertIsInstance(first, ast.Raise)
                self.assertIsInstance(first.exc, ast.Call)
                self.assertIsInstance(first.exc.func, ast.Name)
                self.assertIn(first.exc.func.id, ("PermissionError", "RuntimeError"))
                self.assertTrue(first.exc.args)
                self.assertIsInstance(first.exc.args[0], ast.Constant)
                self.assertEqual(first.exc.args[0].value, marker)

    def test_paper_gateway_requires_explicit_filled(self):
        tree = ast.parse(source(GATEWAY))
        submit = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "submit_order")
        conditions = [n.test for n in ast.walk(submit) if isinstance(n, ast.If)]
        self.assertTrue(any(
            any(isinstance(n, ast.Compare) and any(isinstance(op, ast.IsNot) for op in n.ops)
                and any(isinstance(c, ast.Constant) and c.value is True for c in n.comparators)
                for n in ast.walk(condition))
            for condition in conditions
        ), "Gateway must reject PAPER fill when not literal True")
        self.assertIn("PAPER_ORDER_ACCEPTED", ast.unparse(submit))
        self.assertIn("PAPER_BROKER_NOT_ACCEPTED", ast.unparse(submit))

    def test_p1505j_parse_only_no_execution(self):
        tree = ast.parse(source(MERGER))
        self.assertIsInstance(tree, ast.Module)
        self.assertTrue(any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "for_src" for t in n.targets) for n in tree.body))

    def test_no_external_imports_in_test(self):
        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        imports = set()
        for n in tree.body:
            if isinstance(n, ast.Import):
                imports.update(a.name.split(".")[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom) and n.module:
                imports.add(n.module.split(".")[0])
        self.assertFalse(imports & {"MetaTrader5", "subprocess", "socket", "requests", "importlib"})

if __name__ == "__main__":
    unittest.main()
