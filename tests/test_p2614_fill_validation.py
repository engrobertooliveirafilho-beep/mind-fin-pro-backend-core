import unittest
from test_p2614_original_integration import simulate_fill, C, F, E

class FillValidation(unittest.TestCase):
    def test_paper_buy(self): self.assertIsNotNone(simulate_fill(E[0],C,F,60))
    def test_paper_sell(self): self.assertIsNotNone(simulate_fill(dict(E[0],direction='SELL_PAPER',family='ATR'),C,F,60))
    def test_real_direction_rejected(self):
        with self.assertRaises(ValueError): simulate_fill(dict(E[0],direction='BUY_REAL'),C,F,60)
    def test_unknown_direction_rejected(self):
        with self.assertRaises(ValueError): simulate_fill(dict(E[0],direction='BOGUS'),C,F,60)
    def test_nan_spread_rejected(self):
        with self.assertRaises(ValueError): simulate_fill(E[0],C,F,60,spread_r=float('nan'))
    def test_negative_commission_rejected(self):
        with self.assertRaises(ValueError): simulate_fill(E[0],C,F,60,commission_r=-1)
    def test_zero_entry_rejected(self):
        c=[dict(x) for x in C];c[61]['open']=0
        with self.assertRaises(ValueError): simulate_fill(E[0],c,F,60)
    def test_nonfinite_exit_rejected(self):
        c=[dict(x) for x in C];c[64]['close']=float('inf')
        with self.assertRaises(ValueError): simulate_fill(E[0],c,F,60)
    def test_bad_atr_rejected(self):
        f={k:dict(v) for k,v in F.items()};f[60]['atr']=float('nan')
        with self.assertRaises(ValueError): simulate_fill(E[0],C,f,60)
    def test_negative_signal_index_rejected(self):
        with self.assertRaises(ValueError): simulate_fill(E[0],C,F,-1)
