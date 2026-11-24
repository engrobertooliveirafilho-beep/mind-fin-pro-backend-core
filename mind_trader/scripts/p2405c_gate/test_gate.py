import unittest
from risk_gate import hard_gate,runtime_allowed
class GateTest(unittest.TestCase):
    def test_invalid_metrics(self):
        base=dict(pf=1.5,winrate=45,expectancy=.01,max_dd_r=18,edge_count=5)
        self.assertTrue(hard_gate(base))
        for k,v in [('pf',999),('pf',float('inf')),('winrate',101),('max_dd_r',-1),('edge_count',5.5),('expectancy',float('nan'))]:
            self.assertFalse(hard_gate(dict(base,**{k:v})))
        self.assertFalse(runtime_allowed())
