import unittest
from reports import rank_results
class TestRanking(unittest.TestCase):
    def test_tiers_and_safety(self):
        base=dict(symbol='EURUSD',timeframe='H1',strategy='EMA_CROSS',params='9,34',trades=40,winrate=45,maxdd=1,netprofit=2,mode='LIVE')
        out=rank_results([dict(base,pf=p) for p in (1.2,1.4,1.7,1.0,999,float('nan'))])
        self.assertEqual([r['tier'] for r in out],list('ABCD'))
        self.assertTrue(all(r['mode']=='PAPER_ONLY' and r['real_orders']=='FORBIDDEN' for r in out))
