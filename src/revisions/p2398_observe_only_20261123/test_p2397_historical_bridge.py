import unittest
import csv
import json
from unittest.mock import patch
from p2397_historical_bridge import evaluate_historical_research
class HistoricalResearchTests(unittest.TestCase):
    def test_original_three_hypotheses_research_only(self):
        result=evaluate_historical_research()
        self.assertEqual(result.decision,'RESEARCH_ONLY')
        self.assertEqual(result.hypotheses,3)
        self.assertFalse(result.allowed_for_runtime)
if __name__=='__main__': unittest.main()
