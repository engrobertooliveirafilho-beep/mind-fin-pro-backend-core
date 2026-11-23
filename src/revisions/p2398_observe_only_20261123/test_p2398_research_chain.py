import json
import unittest
from pathlib import Path
from unittest.mock import patch
from p2398_research_chain import evaluate_research_chain
from p2398_observe_gate import GateRejected
from p2397_research_gate import ResearchDecision

HERE = Path(__file__).resolve().parent

class ResearchChainTests(unittest.TestCase):
    def setUp(self):
        self.p = json.loads((HERE / 'p2394_original_summary.json').read_text(encoding='utf-8'))
        self.r = json.loads((HERE / 'router_contract.json').read_text(encoding='utf-8'))
        self.e = json.loads((HERE / 'ensemble_result.json').read_text(encoding='utf-8'))

    def test_originals_research_only(self):
        result = evaluate_research_chain(self.p, self.r, self.e)
        self.assertEqual(result.decision, 'RESEARCH_ONLY')
        self.assertFalse(result.runtime_promotion)
        self.assertFalse(result.order_dispatch)
        self.assertEqual(result.hypotheses, 3)

    def test_p2394_source_mismatch_rejected(self):
        bad = {**self.p, 'score_threshold': 69}
        with self.assertRaises(GateRejected):
            evaluate_research_chain(bad, self.r, self.e)

    def test_p2394_original_artifact_tamper_rejected(self):
        from unittest.mock import patch
        from pathlib import Path
        original = Path.read_bytes
        def forged_bytes(path):
            if path.name == 'p2394_original_summary.json':
                return original(path) + b' '
            return original(path)
        with patch('pathlib.Path.read_bytes', autospec=True, side_effect=forged_bytes):
            with self.assertRaises(GateRejected):
                evaluate_research_chain(self.p, self.r, self.e)

    def test_p2397_rejected_blocks_chain(self):
        with patch('p2398_research_chain.evaluate_historical_research',
                   return_value=ResearchDecision(False, False, 'BLOCK', 'INVALID_RESEARCH_EVIDENCE', 0)):
            with self.assertRaises(GateRejected):
                evaluate_research_chain(self.p, self.r, self.e)

    def test_p2398_bad_quorum_blocks_chain(self):
        with self.assertRaises(GateRejected):
            evaluate_research_chain(self.p, self.r, {**self.e, 'operational_members': 1})

    def test_p2394_promoted_edge_blocks_chain(self):
        bad = {**self.p, 'best_scored_edge': {**self.p['best_scored_edge'], 'decision': 'PROMOTE_SCORE'}}
        with self.assertRaises(GateRejected):
            evaluate_research_chain(bad, self.r, self.e)

if __name__ == '__main__':
    unittest.main()
