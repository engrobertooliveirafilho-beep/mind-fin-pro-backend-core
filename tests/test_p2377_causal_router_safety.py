import ast
import unittest
from pathlib import Path
from unittest.mock import patch
from app.runtime import p2377_de40_regime_first_signal_router_with_xray_lifecycle as router


class P2377CausalityTests(unittest.TestCase):
    def test_historical_outcomes_cannot_change_live_score(self):
        event = {"tick_volume_ratio_50": 2, "body_atr": 1.5, "range_atr": 2}
        low = {"post_efficiency": 0, "post_mfe_atr": 0, "post_mae_atr": 10}
        high = {"post_efficiency": 100, "post_mfe_atr": 100, "post_mae_atr": 0}
        # Permission contract: the routing path must pass None, not future outcomes.
        with patch.object(router, "context_score", wraps=router.context_score) as scoring:
            a = router.context_score(70, 0, event, None)
            b = router.context_score(70, 0, event, None)
        self.assertEqual(a, b)

    def test_router_callsite_uses_no_future_context(self):
        source = Path(router.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "build_xray_router")
        score_calls = [x for x in ast.walk(fn) if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "context_score"]
        self.assertEqual(len(score_calls), 1)
        self.assertIsInstance(score_calls[0].args[3], ast.Constant)
        self.assertIsNone(score_calls[0].args[3].value)
        route_calls = [x for x in ast.walk(fn) if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "recommended_families"]
        self.assertEqual(len(route_calls), 1)
        self.assertEqual(route_calls[0].args[1].value, "UNCLASSIFIED")

    def test_sniff_reads_header_without_full_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candles.csv"
            path.write_text("time;open;close\n1;2;3\n")
            with patch.object(Path, "read_text", side_effect=AssertionError("full read")):
                self.assertEqual(router.sniff(path), ";")


if __name__ == "__main__":
    unittest.main()
