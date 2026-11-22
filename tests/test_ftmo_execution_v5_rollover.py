"""FTMO V5 PAPER day-rollover regression; original Drive dependencies required."""
import unittest
from datetime import date, datetime
from ftmo_paper_guard import D, Rules
from ftmo_pretrade_v2 import OrderIntent
from portfolio_runtime import PaperPortfolio
from app.runtime.ftmo_execution_v5 import ExecutionV5

class V5RolloverTests(unittest.TestCase):
    def setUp(self):
        self.p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        self.k=self.p.open(OrderIntent('BUY',D(100),D(95),D(1),D(1)))
        self.x=ExecutionV5(self.p)
        self.bar=dict(open=100,high=102,low=99,close=101,target=110)

    def test_invalid_ohlc_does_not_advance_day(self):
        with self.assertRaises(ValueError):
            self.x.process_bar({self.k:{**self.bar,'low':103}},day=date(2026,10,30))
        self.assertEqual(self.p.account.day,date(2026,10,29))

    def test_missing_target_does_not_advance_day(self):
        with self.assertRaises(ValueError):
            self.x.process_bar({self.k:{k:v for k,v in self.bar.items() if k!='target'}},day=date(2026,10,30))
        self.assertEqual(self.p.account.day,date(2026,10,29))

    def test_invalid_day_does_not_mutate(self):
        with self.assertRaises(ValueError):
            self.x.process_bar({self.k:self.bar},day='2026-10-30')
        self.assertEqual(self.p.account.day,date(2026,10,29))

    def test_valid_rollover(self):
        result=self.x.process_bar({self.k:self.bar},day=date(2026,10,30))
        self.assertEqual(self.p.account.day,date(2026,10,30))
        self.assertEqual(result['real_orders'],0)

    def test_time_reversal(self):
        with self.assertRaises(ValueError):
            self.x.process_bar({self.k:self.bar},day=date(2026,10,28))
        self.assertEqual(self.p.account.day,date(2026,10,29))
