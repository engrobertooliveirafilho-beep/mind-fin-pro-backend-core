"""ET668: static integration contract across historical S11, S15-S17 and ET667.
Never imports or runs historical executors, brokers or the canonical runtime.
"""
import ast
import pathlib
import unittest

BASE = pathlib.Path(__file__).resolve().parents[1] / "historical"
SOURCES = {
    "S11": BASE / "s_stages/S11/controlled_runtime_materialization_probe.py",
    "S15": BASE / "s_stages/S15/supervised_continuous_paper_runtime.py",
    "S16": BASE / "s_stages/S16/extended_supervised_paper_market_replay.py",
    "S17": BASE / "s_stages/S17/simulator_activation_candidate_feed.py",
}
DERIVED = BASE / "derived/et667/mind_trader_institutional_wiring.py"

class ET668HistoricalContract(unittest.TestCase):
    def test_original_executors_reference_factory(self):
        for stage, path in SOURCES.items():
            with self.subTest(stage=stage):
                code = path.read_text(encoding="utf-8")
                ast.parse(code, filename=str(path))
                self.assertIn("create_paper_runtime", code)
                self.assertIn("app.runtime.mind_trader_institutional_wiring", code)

    def test_derived_factory_has_no_dispatch(self):
        tree = ast.parse(DERIVED.read_text(encoding="utf-8"))
        names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.assertIn("create_paper_runtime", names)
        self.assertIn("health", names)
        self.assertFalse(names.intersection({"start", "run", "send_order", "execute_order", "connect_broker"}))

    def test_derived_status_does_not_claim_runtime_certification(self):
        content = DERIVED.read_text(encoding="utf-8")
        self.assertIn("COMPATIBILITY_ONLY", content)
        self.assertIn("historical_runtime_recovered", content)
        self.assertIn("False", content)

    def test_canonical_runtime_is_not_in_archive(self):
        self.assertFalse((BASE / "app/runtime/mind_trader_institutional_wiring.py").exists())

if __name__ == "__main__":
    unittest.main()
