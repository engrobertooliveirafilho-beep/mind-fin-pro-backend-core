import unittest
from datetime import datetime,timezone
from mind_trader.research.et665_r436_p2408_safe_adapter import dispatch_paper
N=datetime(2026,11,10,12,tzinfo=timezone.utc);T=N.isoformat()
P=dict(mode='PAPER_ONLY',real_orders='FORBIDDEN',ftmo_real='FORBIDDEN',real_execution_allowed=False,allowed_symbol='GER40',allowed_timeframes=['M15'],allowed_sessions=['US_MORNING'],allowed_regimes=['TREND_UP'],min_context_matches=2,min_weight_sum=.4,min_confidence=.62)
C=dict(symbol='GER40',timeframe='M15',session='US_MORNING',regime='TREND_UP',direction='BUY_PAPER',timestamp=T)
V=[dict(edge_id=i,direction='BUY_PAPER',symbol='GER40',timeframe='M15',weight=.35,timestamp=T) for i in ('a','b')]
def legacy(c):return {'allowed':True,'route':'PAPER_SIGNAL_CANDIDATE','real_execution_allowed':False}
class TestPackageAdapter(unittest.TestCase):
 def test_valid_paper(self):self.assertTrue(dispatch_paper(C,V,P,legacy,N)['allowed'])
 def test_missing_direction(self):self.assertFalse(dispatch_paper({k:v for k,v in C.items() if k!='direction'},V,P,legacy,N)['allowed'])
 def test_opposite(self):self.assertFalse(dispatch_paper(dict(C,direction='SELL_PAPER'),V,P,legacy,N)['allowed'])
 def test_missing_votes(self):self.assertFalse(dispatch_paper(C,[],P,legacy,N)['allowed'])
 def test_legacy_failure(self):self.assertFalse(dispatch_paper(C,V,P,lambda _: {'allowed':False},N)['allowed'])
 def test_legacy_exception(self):self.assertFalse(dispatch_paper(C,V,P,lambda _:1/0,N)['allowed'])
 def test_live_policy(self):self.assertFalse(dispatch_paper(C,V,dict(P,real_orders='ALLOWED'),legacy,N)['allowed'])
 def test_legacy_missing_safety(self):self.assertFalse(dispatch_paper(C,V,P,lambda _: {'allowed':True},N)['allowed'])
if __name__=='__main__':unittest.main()
