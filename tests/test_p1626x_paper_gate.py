import unittest
from app.runtime.p1626x_paper_gate import validate

def edge():return {'edge_id':'A','profit_factor':2,'max_drawdown':0.2,'decay_revalidation_score':0.1}
class TestGate(unittest.TestCase):
    def test_valid(self):self.assertEqual(validate([edge()])['edges'],1)
    def test_no_e2e(self):self.assertFalse(validate([edge()])['e2e_certified'])
    def test_no_orders(self):self.assertFalse(validate([edge()])['order_send_allowed'])
    def test_no_correlation_claim(self):self.assertFalse(validate([edge()])['correlation_estimated'])
    def test_missing(self):
        with self.assertRaises(ValueError):validate([])
    def test_duplicate(self):
        with self.assertRaises(ValueError):validate([edge(),edge()])
    def test_nan(self):
        e=edge();e['profit_factor']='NaN'
        with self.assertRaises(ValueError):validate([e])
    def test_negative_pf(self):
        e=edge();e['profit_factor']=-1
        with self.assertRaises(ValueError):validate([e])
    def test_drawdown(self):
        e=edge();e['max_drawdown']=2
        with self.assertRaises(ValueError):validate([e])
    def test_decay(self):
        e=edge();e['decay_revalidation_score']=-0.1
        with self.assertRaises(ValueError):validate([e])
    def test_missing_metric(self):
        e=edge();del e['profit_factor']
        with self.assertRaises(ValueError):validate([e])
    def test_boolean(self):
        e=edge();e['max_drawdown']=False
        with self.assertRaises(ValueError):validate([e])
