"""P2288C research-only regression tests; no runtime/broker imports."""
import csv
import tempfile
import unittest
from pathlib import Path
from mind_trader.research.p2288c_corrected import load_strict,unique_candidates,backtest,evaluate


class CorrectedTests(unittest.TestCase):
    def setUp(self):
        self.q={'symbol':'GER40','timeframe':'H1','strategy':'SESSION_TREND','session_filter':'ANY','volatility_filter':'ANY','spread_filter':'ANY','trend_filter':'ANY','mode':'PAPER_ONLY','real_orders':'FORBIDDEN'}
        self.rows=[{'time':str(i),'open':100+i,'close':101+i,'session':'NY','volatility_state':'HIGH','spread_state':'NORMAL','trend_9_21':'UP','trend_21_55':'UP','trend_55_200':'UP'} for i in range(1200)]
    def test_dedup(self):
        self.assertEqual(len(unique_candidates([dict(self.q,fast='5'),dict(self.q,fast='9')])),1)
    def test_reject_live(self):
        with self.assertRaises(ValueError):unique_candidates([dict(self.q,real_orders='ALLOWED')])
    def test_cost_required(self):
        with self.assertRaises(ValueError):backtest(self.rows,self.q,None)
    def test_terminal_close(self):
        self.assertEqual(backtest(self.rows[:3],self.q,0)['trades'],1)
    def test_cost_reduces_net(self):
        a=backtest(self.rows,self.q,0);b=backtest(self.rows,self.q,0.5)
        self.assertAlmostEqual(a['netprofit']-b['netprofit'],0.5*a['trades'])
    def test_no_cost_model(self):
        with self.assertRaises(ValueError):evaluate([self.q],{('GER40','H1'):self.rows},{})
    def test_no_approval(self):
        x=evaluate([self.q],{('GER40','H1'):self.rows},{'GER40':0.1})
        self.assertFalse(x[0]['financial_certified'])
        self.assertNotIn('APPROVED',x[0]['status'])
    def test_strict_bad_row(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.csv'
            with p.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(self.rows[0]));w.writeheader();w.writerow(dict(self.rows[0],open='bad'))
            with self.assertRaisesRegex(ValueError,'line 2'):load_strict(p)
    def test_invalid_cost(self):
        with self.assertRaises(ValueError):backtest(self.rows,self.q,-1)


if __name__=='__main__':unittest.main()
