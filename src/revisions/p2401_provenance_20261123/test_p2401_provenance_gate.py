import unittest
from pathlib import Path
from p2401_provenance_gate import classify_source

class ProvenanceTests(unittest.TestCase):
    def test_original_synthetic(self):
        r=classify_source(Path(__file__).with_name('p2401_multi_edge_walk_forward_dd_filter.py'))
        self.assertTrue(r['synthetic_metrics'])
        self.assertFalse(r['historical_market_data_evidenced'])
        self.assertFalse(r['performance_certified'])
        self.assertFalse(r['runtime_promotion_allowed'])
    def test_safe_source(self):
        self.assertFalse(classify_source(Path(__file__).with_name('p2401_provenance_gate.py'))['synthetic_metrics'])
if __name__=='__main__': unittest.main()
