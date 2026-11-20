import copy
import unittest
from app.runtime.p1636_research_gate import reconcile

class TestP1636ResearchGate(unittest.TestCase):
    def setUp(self):
        self.loop={'STATUS':'P1636_SELF_LEARNING_RESEARCH_LOOP_REGISTERED',
          'LOOP':['DISCOVER','BACKTEST','VALIDATE','CATALOG_SPECIALIST','CLASSIFY_REGIME','MINE_CONFLUENCE','PROMOTE','QUARANTINE_WEAK_SPECIALISTS'],
          'NEXT':'ADD_P1625_TO_P1636_TO_DAILY_ORCHESTRATOR',
          'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}
        self.portfolio={'DECISION':'WATCH_ONLY','ORDER_SENT':False,'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}
        self.evolution=[{'specialist_id':'A'}]
    def run_gate(self):
        return reconcile(self.loop,self.portfolio,self.evolution)
    def test_reconciled(self):
        self.assertEqual(self.run_gate()['status'],'RESEARCH_ONLY_RECONCILED')
    def test_no_orders(self):
        self.assertFalse(self.run_gate()['order_send_allowed'])
    def test_no_promotion(self):
        self.assertNotIn('PROMOTE',self.run_gate()['permitted_stages'])
    def test_no_orchestrator(self):
        self.assertFalse(self.run_gate()['orchestrator_connected'])
    def test_no_e2e(self):
        self.assertFalse(self.run_gate()['e2e_certified'])
    def test_tampered_stages(self):
        self.loop['LOOP'].remove('VALIDATE')
        with self.assertRaises(ValueError):self.run_gate()
    def test_tampered_order_flags(self):
        self.loop['REAL_ORDERS']='ALLOWED'
        with self.assertRaises(ValueError):self.run_gate()
    def test_portfolio_sent(self):
        self.portfolio['ORDER_SENT']=True
        with self.assertRaises(ValueError):self.run_gate()
    def test_duplicate_specialists(self):
        self.evolution.append(copy.deepcopy(self.evolution[0]))
        with self.assertRaises(ValueError):self.run_gate()
    def test_no_evidence(self):
        self.evolution=[]
        with self.assertRaises(ValueError):self.run_gate()
