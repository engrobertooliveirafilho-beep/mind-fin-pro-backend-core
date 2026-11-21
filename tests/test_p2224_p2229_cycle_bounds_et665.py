"""ET665 offline cycle-bound regressions for two original PAPER simulation engines."""
import unittest
from app.runtime import p2224_2226_institutional_core as core
from app.runtime import p2227_2229_advanced_layer as advanced
class SimulationCycleBoundsTests(unittest.TestCase):
    def test_core_zero(self):
        with self.assertRaises(ValueError): core.run(0)
    def test_core_negative(self):
        with self.assertRaises(ValueError): core.run(-1)
    def test_core_bool(self):
        with self.assertRaises(TypeError): core.run(True)
    def test_core_one_cycle(self):
        self.assertEqual(core.run(1)['cycles'],1)
    def test_advanced_zero(self):
        with self.assertRaises(ValueError): advanced.run(0)
    def test_advanced_negative(self):
        with self.assertRaises(ValueError): advanced.run(-1)
    def test_advanced_bool(self):
        with self.assertRaises(TypeError): advanced.run(True)
    def test_advanced_one_cycle(self):
        self.assertEqual(advanced.run(1)['cycles'],1)
if __name__=='__main__':unittest.main()
