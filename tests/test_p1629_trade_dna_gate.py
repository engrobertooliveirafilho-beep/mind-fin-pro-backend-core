import unittest
from app.runtime.p1629_trade_dna_gate import audit

def row():
    return {'specialist_id':'X_abc','edge_id':'abc','dna_status':'TRADE_DNA_REGISTERED',
            'regime_tags':['RANGE'],'best_entry_hour':12,'payoff_ratio_real':2,
            'expectancy_per_trade_real':0.01,'profit_factor_real':2,
            'avg_holding_bars':3,'avg_R':1,'max_R':4,'p90_R':None}
class TestP1629(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(audit([row()])['records'],1)
    def test_missing_p90_disclosed(self):
        self.assertEqual(audit([row()])['missing_p90_R'],1)
    def test_incomplete(self):
        self.assertFalse(audit([row()])['statistics_complete'])
    def test_no_orders(self):
        self.assertFalse(audit([row()])['order_send_allowed'])
    def test_no_e2e(self):
        self.assertFalse(audit([row()])['e2e_certified'])
    def test_duplicate(self):
        with self.assertRaises(ValueError):audit([row(),row()])
    def test_nan(self):
        r=row();r['avg_R']='NaN'
        with self.assertRaises(ValueError):audit([r])
    def test_bad_hour(self):
        r=row();r['best_entry_hour']=24
        with self.assertRaises(ValueError):audit([r])
    def test_missing(self):
        with self.assertRaises(ValueError):audit([])
    def test_bad_status(self):
        r=row();r['dna_status']='PROMOTED'
        with self.assertRaises(ValueError):audit([r])
    def test_negative(self):
        r=row();r['profit_factor_real']=-1
        with self.assertRaises(ValueError):audit([r])
