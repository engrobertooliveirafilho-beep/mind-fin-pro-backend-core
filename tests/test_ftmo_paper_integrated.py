"""Offline package integration: recovered FTMO PAPER guard -> pretrade -> portfolio -> V5."""
import unittest
from datetime import date
from app.runtime.ftmo_paper_guard import D, Rules
from app.runtime.ftmo_pretrade_v2 import OrderIntent
from app.runtime.portfolio_runtime import PaperPortfolio
from app.runtime.ftmo_execution_v5 import ExecutionV5

class IntegratedPaperTests(unittest.TestCase):
    def test_open_mark_exit_and_rollover_without_broker(self):
        p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        a=p.open(OrderIntent('BUY',D(100),D(95),D(1),D(1)))
        b=p.open(OrderIntent('BUY',D(100),D(95),D(1),D(1)))
        self.assertIsNotNone(a)
        self.assertIsNotNone(b)
        bars={a:dict(open=100,high=111,low=99,close=108,target=110),
              b:dict(open=100,high=104,low=99,close=104,target=110)}
        result=ExecutionV5(p).process_bar(bars,day=date(2026,10,30))
        self.assertEqual(result['exits'],1)
        self.assertEqual(result['open'],1)
        self.assertEqual(p.account.equity,D(100014))
        self.assertEqual(p.account.day,date(2026,10,30))
        self.assertEqual(result['real_orders'],0)
        self.assertTrue(any(e['event']=='MARK' for e in p.audit))
        self.assertTrue(any(e['event']=='AUTO_EXIT' for e in p.audit))
    def test_invalid_bar_cannot_advance_account_day(self):
        p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        a=p.open(OrderIntent('BUY',D(100),D(95),D(1),D(1)))
        with self.assertRaises(ValueError):
            ExecutionV5(p).process_bar({a:dict(open=100,high=99,low=101,close=100,target=110)},day=date(2026,10,30))
        self.assertEqual(p.account.day,date(2026,10,29))

    def test_malformed_bar_is_fail_closed_without_mutation(self):
        p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        a=p.open(OrderIntent('BUY',D(100),D(95),D(1),D(1)))
        before=(p.account.balance,p.account.equity,len(p.audit),p.account.day)
        for bad in [None, {}, {'open': 100}, {'open':'not-a-number','high':101,'low':99,'close':100,'target':110}]:
            with self.assertRaises(ValueError):
                ExecutionV5(p).process_bar({a:bad})
            self.assertEqual((p.account.balance,p.account.equity,len(p.audit),p.account.day),before)
