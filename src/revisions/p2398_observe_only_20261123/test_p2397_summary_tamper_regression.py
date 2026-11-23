import json
import unittest
from unittest.mock import patch
from p2397_historical_bridge import HERE, evaluate_historical_research

class SummaryTamperRegression(unittest.TestCase):
    def test_historical_summary_runtime_promotion_rejected(self):
        original = json.loads((HERE / 'p2394_original_summary.json').read_text(encoding='utf-8'))
        policy = json.loads((HERE / 'p2397_original_policy.json').read_text(encoding='utf-8'))
        summary = json.loads((HERE / 'p2397_original_summary.json').read_text(encoding='utf-8'))
        summary['runtime_promotion_allowed'] = True
        with patch('p2397_historical_bridge.json.loads', side_effect=[original, policy, summary]):
            result = evaluate_historical_research()
        self.assertEqual(result.decision, 'BLOCK')
        self.assertFalse(result.allowed_for_runtime)

if __name__ == '__main__':
    unittest.main()
