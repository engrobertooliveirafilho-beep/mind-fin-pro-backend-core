import unittest
from pathlib import Path
from provenance import certify
class Tests(unittest.TestCase):
    def test_original_hash_sampling(self):
        self.assertTrue(certify(Path(__file__).with_name("p2403e_rebuild_de40_replay_series.py"))["hash_sampled"])
    def test_correlation_block(self):
        self.assertFalse(certify(Path(__file__).with_name("p2403e_rebuild_de40_replay_series.py"))["portfolio_correlation_certified"])
    def test_runtime_block(self):
        self.assertFalse(certify(Path(__file__).with_name("p2403e_rebuild_de40_replay_series.py"))["runtime_promotion_allowed"])
if __name__=="__main__":unittest.main()
