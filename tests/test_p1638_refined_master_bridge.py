import copy
import unittest
from app.runtime.p1638_refined_master_bridge import bridge

class P1638BridgeTests(unittest.TestCase):
    def setUp(self):
        self.row={'specialist_id':'A','hour':20,'deployment_score':50,'confluence_score':50,
          'refined_session':'NEW_YORK','session_bonus':7,'refined_opportunity_score':52,
          'refined_decision':'WATCH_ONLY','decision':'WATCH_ONLY','ORDER_SENT':False,
          'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}
        self.report={'OPPORTUNITIES_REFINED':1,'SESSIONS_REGISTERED':1,
          'ELITE_CANDIDATES':0,'DEMO_CANDIDATES':0,'WATCH_HIGH_PRIORITY':0,
          'TOP10_REFINED':[self.row],'ORDER_SENT':False,'REAL_ORDERS':'FORBIDDEN',
          'FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}
        self.master={'BEST_CURRENT_OPPORTUNITY':{'specialist_id':'A'},
          'DECISION':'WATCH_ONLY','ORDER_SENT':False,'REAL_ORDERS':'FORBIDDEN',
          'FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}
    def run_bridge(self):
        return bridge([self.row],[{'session':'NEW_YORK'}],self.report,self.master)
    def test_reconciled(self):
        self.assertEqual(self.run_bridge()['status'],'P1638_BRIDGE_OFFLINE_ONLY')
    def test_no_orders(self):
        self.assertFalse(self.run_bridge()['order_send_allowed'])
    def test_no_e2e(self):
        self.assertFalse(self.run_bridge()['e2e_certified'])
    def test_conflict(self):
        self.master['BEST_CURRENT_OPPORTUNITY']['specialist_id']='B'
        self.assertEqual(self.run_bridge()['status'],'RECONCILIATION_CONFLICT')
    def test_reject_order(self):
        self.master['ORDER_SENT']=True
        with self.assertRaises(ValueError):self.run_bridge()
    def test_reject_promoted(self):
        self.row['refined_decision']='ELITE_CANDIDATE'
        with self.assertRaises(ValueError):self.run_bridge()
