"""Offline regression against recovered historical P1635/P1637 artifacts.
Run with ELDORA_HISTORICAL_DIR pointing at the recovered evidence directory.
"""
import copy
import json
import os
import unittest
from pathlib import Path
from app.runtime.p1638_refined_master_bridge import bridge

DATA = Path(os.environ.get('ELDORA_HISTORICAL_DIR', '/mnt/data'))
class HistoricalBridgeRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names=('refined_opportunity_ranking.json','refined_session_library.json',
               'p1637_session_threshold_report.json','p1635_master_portfolio_brain.json')
        if not all((DATA/name).is_file() for name in names):
            raise unittest.SkipTest('original historical artifacts unavailable; no synthetic substitution')
        cls.rows=json.loads((DATA/names[0]).read_text())
        cls.sessions=json.loads((DATA/names[1]).read_text())
        cls.report=json.loads((DATA/names[2]).read_text())
        cls.master=json.loads((DATA/names[3]).read_text())
    def test_original_conflict(self):
        r=bridge(self.rows,self.sessions,self.report,self.master)
        self.assertEqual(r['status'],'RECONCILIATION_CONFLICT')
        self.assertFalse(r['order_send_allowed'])
    def test_consistent_snapshot_still_offline(self):
        m=copy.deepcopy(self.master)
        m['BEST_CURRENT_OPPORTUNITY'].update({k:self.rows[0][k] for k in ('specialist_id','asset','timeframe')})
        r=bridge(self.rows,self.sessions,self.report,m)
        self.assertEqual(r['status'],'P1638_BRIDGE_OFFLINE_ONLY')
        self.assertFalse(r['order_send_allowed'])
        self.assertFalse(r['e2e_certified'])
    def test_same_specialist_wrong_asset_rejected(self):
        m=copy.deepcopy(self.master)
        m['BEST_CURRENT_OPPORTUNITY'].update({k:self.rows[0][k] for k in ('specialist_id','asset','timeframe')})
        m['BEST_CURRENT_OPPORTUNITY']['asset']='GBPUSD'
        self.assertEqual(bridge(self.rows,self.sessions,self.report,m)['status'],'RECONCILIATION_CONFLICT')
    def test_same_specialist_wrong_timeframe_rejected(self):
        m=copy.deepcopy(self.master)
        m['BEST_CURRENT_OPPORTUNITY'].update({k:self.rows[0][k] for k in ('specialist_id','asset','timeframe')})
        m['BEST_CURRENT_OPPORTUNITY']['timeframe']='M1'
        self.assertEqual(bridge(self.rows,self.sessions,self.report,m)['status'],'RECONCILIATION_CONFLICT')
    def test_historical_winner_is_rank_two(self):
        r=bridge(self.rows,self.sessions,self.report,self.master)
        self.assertEqual(r['historical_best_refined_rank'],2)
        self.assertEqual(r['refined_top_specialist_id'],self.rows[0]['specialist_id'])
        self.assertFalse(r['order_send_allowed'])
    def test_unknown_historical_identity_no_rank(self):
        m=copy.deepcopy(self.master)
        m['BEST_CURRENT_OPPORTUNITY']['specialist_id']='UNKNOWN'
        r=bridge(self.rows,self.sessions,self.report,m)
        self.assertIsNone(r['historical_best_refined_rank'])
        self.assertFalse(r['promotion_allowed'])
    def test_ambiguous_identity_rejected(self):
        rows=copy.deepcopy(self.rows)
        rows[2]['specialist_id']=rows[1]['specialist_id']
        with self.assertRaises(ValueError):bridge(rows,self.sessions,self.report,self.master)
    def test_master_best_candidate_must_be_watch_only(self):
        m=copy.deepcopy(self.master)
        m['BEST_CURRENT_OPPORTUNITY']['decision']='BUY'
        with self.assertRaises(ValueError):
            bridge(self.rows,self.sessions,self.report,m)
    def test_master_best_requires_explicit_decision(self):
        m=copy.deepcopy(self.master)
        del m['BEST_CURRENT_OPPORTUNITY']['decision']
        with self.assertRaises(ValueError):
            bridge(self.rows,self.sessions,self.report,m)
    def test_unsafe_master_rejected(self):
        m=copy.deepcopy(self.master);m['ORDER_SENT']=True
        with self.assertRaises(ValueError):bridge(self.rows,self.sessions,self.report,m)
    def test_unsafe_real_flag_rejected(self):
        m=copy.deepcopy(self.master);m['REAL_ORDERS']='ALLOWED'
        with self.assertRaises(ValueError):bridge(self.rows,self.sessions,self.report,m)
if __name__=='__main__':unittest.main()
