import unittest
from app.runtime.step210_creative_dna_safe import SafeCreativeDNAEngine

class CreativeDNATests(unittest.TestCase):
    def setUp(self): self.engine=SafeCreativeDNAEngine('brand-a','seed-a')
    def test_deterministic(self): self.assertEqual(self.engine.get_dna()['traits'],SafeCreativeDNAEngine('brand-a','seed-a').get_dna()['traits'])
    def test_eight_traits(self): self.assertEqual(len(self.engine.get_dna()['traits']),8)
    def test_nudge(self): self.assertEqual(self.engine.nudge({'boldness':0.1})['history_length'],2)
    def test_nan_nudge_atomic(self):
        before=self.engine.get_dna()
        with self.assertRaises(ValueError): self.engine.nudge({'boldness':0.1,'warmth':float('nan')})
        self.assertEqual(before,self.engine.get_dna())
    def test_inf_nudge(self):
        with self.assertRaises(ValueError): self.engine.nudge({'boldness':float('inf')})
    def test_unknown_trait(self):
        with self.assertRaises(ValueError): self.engine.nudge({'unknown':1})
    def test_blend_valid(self): self.assertEqual(self.engine.blend_with({'traits':{'boldness':0.8}})['history_length'],2)
    def test_blend_nan_atomic(self):
        before=self.engine.get_dna()
        with self.assertRaises(ValueError): self.engine.blend_with({'traits':{'boldness':float('nan')}})
        self.assertEqual(before,self.engine.get_dna())
    def test_blend_inf_weight(self):
        with self.assertRaises(ValueError): self.engine.blend_with({'traits':{}},float('inf'))
    def test_not_finance(self): self.assertEqual(self.engine.version,'step210-v1')
