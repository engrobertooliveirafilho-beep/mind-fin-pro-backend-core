import unittest
from pathlib import Path
from p2403b_provenance_gate import inspect_replay_builder
class Tests(unittest.TestCase):
    def test_original_repair_is_hash_sampled(self):
        r=inspect_replay_builder(Path(__file__).with_name('p2403b_repair.py'))
        self.assertTrue(r['hash_seeded_sampling'])
        self.assertFalse(r['strategy_signals_verified'])
    def test_no_certification(self):
        r=inspect_replay_builder(Path(__file__).with_name('p2403b_repair.py'))
        self.assertFalse(r['strategy_performance_certified'])
        self.assertFalse(r['runtime_promotion_allowed'])
if __name__=='__main__': unittest.main()
