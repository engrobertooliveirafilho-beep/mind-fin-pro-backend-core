import unittest
from unittest.mock import patch
from app.runtime.p2362_full_signal_decision_pipeline import decide_signal


class P2362EnvelopeTests(unittest.TestCase):
    @patch("app.runtime.p2362_full_signal_decision_pipeline.classify_context_edge")
    def test_non_dict_envelopes_fail_closed_before_engine(self, edge):
        for signal, context in ((None, {}), ({}, None), ("BUY", {}), ({}, [])):
            with self.subTest(signal=signal, context=context):
                result = decide_signal(signal, context)
                self.assertEqual(result["final_decision"], "BLOCK_INVALID_ENVELOPE")
                self.assertEqual(result["paper_lot"], 0)
                self.assertEqual(result["real_orders"], "FORBIDDEN")
                self.assertEqual(result["ftmo_real"], "FORBIDDEN")
        edge.assert_not_called()


if __name__ == "__main__":
    unittest.main()
