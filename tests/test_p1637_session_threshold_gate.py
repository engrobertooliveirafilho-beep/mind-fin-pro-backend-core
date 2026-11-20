import unittest
from app.runtime.p1637_session_threshold_gate import reconcile,session
def row():
    return {'specialist_id':'EURUSD_H1_A','hour':20,'deployment_score':50,'confluence_score':50,'refined_session':'NEW_YORK','session_bonus':7,'refined_opportunity_score':52,'refined_decision':'WATCH_ONLY','decision':'WATCH_ONLY','ORDER_SENT':False,'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}
def report(r):
    return {'OPPORTUNITIES_REFINED':1,'SESSIONS_REGISTERED':1,'ELITE_CANDIDATES':0,'DEMO_CANDIDATES':0,'WATCH_HIGH_PRIORITY':0,'TOP10_REFINED':[r],'ORDER_SENT':False,'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}
class TestP1637(unittest.TestCase):
    def test_valid(self):
        r=row();self.assertEqual(reconcile([r],[{'session':'NEW_YORK'}],report(r))['rows'],1)
    def test_orders_forbidden(self):
        r=row();self.assertFalse(reconcile([r],[{}],report(r))['order_send_allowed'])
    def test_e2e_false(self):
        r=row();self.assertFalse(reconcile([r],[{}],report(r))['e2e_certified'])
    def test_bad_hour(self):
        with self.assertRaises(ValueError):session(24)
    def test_bool_hour(self):
        with self.assertRaises(ValueError):session(True)
    def test_tamper(self):
        r=row();p=report(r);r['refined_opportunity_score']=53
        with self.assertRaises(ValueError):reconcile([r],[{}],p)
    def test_unauthorized_order(self):
        r=row();r['ORDER_SENT']=True
        with self.assertRaises(ValueError):reconcile([r],[{}],report(r))
    def test_duplicate(self):
        r=row()
        with self.assertRaises(ValueError):reconcile([r,r],[{}],report(r))
    def test_missing(self):
        with self.assertRaises(ValueError):reconcile([],[],{})
    def test_report_mismatch(self):
        r=row();p=report(r);p['OPPORTUNITIES_REFINED']=2
        with self.assertRaises(ValueError):reconcile([r],[{}],p)

    def test_report_aggregate_schema(self):
        r=row();r.update(deployment_score=100,confluence_score=100,refined_opportunity_score=97,refined_decision='ELITE_CANDIDATE')
        p=report(r);p['ELITE_CANDIDATES']=1
        self.assertEqual(reconcile([r],[{}],p)['rows'],1)
    def test_reject_aggregate_tampering(self):
        r=row();p=report(r);p['DEMO_CANDIDATES']=1
        with self.assertRaises(ValueError):reconcile([r],[{}],p)
