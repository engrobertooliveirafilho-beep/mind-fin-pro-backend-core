import unittest
from app.runtime.p1625_safe_portfolio import allocate

def row():return {'edge_id':'E1','profit_factor':2,'max_drawdown':0.2,'decay_revalidation_score':0.1}
class TestP1625(unittest.TestCase):
    def test_valid(self):self.assertEqual(allocate([row()])[0]['paper_weight'],1)
    def test_no_orders(self):self.assertEqual(allocate([row()])[0]['REAL_ORDERS'],'FORBIDDEN')
    def test_missing(self):
        with self.assertRaises(ValueError):allocate([])
    def test_duplicate(self):
        with self.assertRaises(ValueError):allocate([row(),row()])
    def test_nan(self):
        r=row();r['profit_factor']=float('nan')
        with self.assertRaises(ValueError):allocate([r])
    def test_inf(self):
        r=row();r['max_drawdown']=float('inf')
        with self.assertRaises(ValueError):allocate([r])
    def test_boolean(self):
        r=row();r['profit_factor']=True
        with self.assertRaises(ValueError):allocate([r])
    def test_negative(self):
        r=row();r['profit_factor']=-1
        with self.assertRaises(ValueError):allocate([r])
    def test_bad_drawdown(self):
        r=row();r['max_drawdown']=2
        with self.assertRaises(ValueError):allocate([r])
    def test_bad_decay(self):
        r=row();r['decay_revalidation_score']=-1
        with self.assertRaises(ValueError):allocate([r])
    def test_weights(self):
        r=row();s=row();s['edge_id']='E2'
        self.assertAlmostEqual(sum(x['paper_weight'] for x in allocate([r,s])),1)
    def test_no_mutation(self):
        r=row();allocate([r]);self.assertNotIn('paper_weight',r)
