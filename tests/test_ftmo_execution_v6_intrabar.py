"""PAPER V6 regressions against recovered original FTMO risk and portfolio."""
import unittest
from datetime import date
from app.runtime.ftmo_paper_guard import D, Rules
from app.runtime.ftmo_pretrade_v2 import OrderIntent
from app.runtime.portfolio_runtime import PaperPortfolio
from app.runtime.ftmo_execution_v6 import ExecutionV6

class V6RiskTests(unittest.TestCase):
    def setUp(self):
        self.p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        self.e=ExecutionV6(self.p)

    def test_intrabar_breach_is_not_sticky_result_flag(self):
        pid=self.p.open(OrderIntent('BUY',D(100),D(90),D(1),D(100)))
        first=self.e.process_bar({pid:dict(open=100,high=105,low=40,close=100,target=120)})
        self.assertTrue(first['intrabar_breach'])
        self.assertTrue(first['halted'])
        second=self.e.process_bar({})
        self.assertFalse(second['intrabar_breach'])
        self.assertEqual(second['real_orders'],0)

    def test_invalid_inputs_do_not_mutate_day_or_audit(self):
        pid=self.p.open(OrderIntent('BUY',D(100),D(90),D(1),D(100)))
        before=(self.p.account.day,self.p.account.balance,len(self.p.audit))
        for bad in [None,{},dict(open=100,high=99,low=101,close=100,target=120),
                    dict(open='NaN',high=105,low=95,close=100,target=120)]:
            with self.assertRaises(ValueError):
                self.e.process_bar({pid:bad},day=date(2026,10,30))
            self.assertEqual((self.p.account.day,self.p.account.balance,len(self.p.audit)),before)

    def test_invalid_day_does_not_mutate(self):
        pid=self.p.open(OrderIntent('BUY',D(100),D(90),D(1),D(100)))
        with self.assertRaises(ValueError):
            self.e.process_bar({pid:dict(open=100,high=105,low=95,close=100,target=120)},day='2026-10-30')
        self.assertEqual(self.p.account.day,date(2026,10,29))
