"""R341: forensic regression tests for historical DE40 source; no strategy promotion."""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "recovery" / "r341_originals"

class HistoricalSourceSafety(unittest.TestCase):
    def test_p2383c_lookahead_is_not_certifiable(self):
        source = (SOURCE / "p2383c_de40_true_out_of_sample_validation.py").read_text()
        tree = ast.parse(source)
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "simulate_signal")
        code = ast.get_source_segment(source, fn)
        self.assertIn('nxt["close"]>=c["close"]', code)
        self.assertIn('direction=1 if', code)
        # Regression detection, not a PASS of the strategy: forward price determines direction.
        self.assertTrue(True, "LOOKAHEAD_DETECTED; promotion forbidden")

    def test_p2382_unconditional_certified_label_detected(self):
        source = (SOURCE / "p2382_de40_replay_after_loss_patch.py").read_text()
        ast.parse(source)
        self.assertIn('"status": "CERTIFIED"', source)
        self.assertIn('"success": success', source)
        self.assertTrue(True, "MISLEADING_CERTIFICATION_LABEL; promotion forbidden")

    def test_p2383_promotion_logic_is_not_authority(self):
        source = (SOURCE / "p2383_de40_walk_forward_after_patch.py").read_text()
        ast.parse(source)
        self.assertIn('return "PROMOTE"', source)
        self.assertIn('MODE = "PAPER_ONLY"', source)

if __name__ == "__main__":
    unittest.main()
