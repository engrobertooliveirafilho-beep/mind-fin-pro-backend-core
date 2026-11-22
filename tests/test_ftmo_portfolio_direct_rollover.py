"""PAPER portfolio direct rollover must reject invalid chronology before mutation."""
import unittest
from datetime import date, datetime
from app.runtime.ftmo_paper_guard import D, Rules
from app.runtime.portfolio_runtime import PaperPortfolio
from app.runtime.ftmo_pretrade_v2 import OrderIntent

class DirectRollover(unittest.TestCase):
    def setUp(self):
        self.p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        self.pid=self.p.open(OrderIntent('BUY',D(100),D(95),D(1),D(1)))
        self.p.positions[self.pid].last_price=D(101)

    def test_datetime_rejected_before_equity_mutation(self):
        before=(self.p.account.equity,self.p.account.day,len(self.p.audit))
        with self.assertRaises(ValueError):
            self.p.new_day(datetime(2026,10,30))
        self.assertEqual((self.p.account.equity,self.p.account.day,len(self.p.audit)),before)

    def test_past_date_rejected_before_equity_mutation(self):
        before=(self.p.account.equity,self.p.account.day,len(self.p.audit))
        with self.assertRaises(ValueError):
            self.p.new_day(date(2026,10,28))
        self.assertEqual((self.p.account.equity,self.p.account.day,len(self.p.audit)),before)

    def test_valid_date_updates_equity(self):
        self.p.new_day(date(2026,10,30))
        self.assertEqual(self.p.account.day,date(2026,10,30))
        self.assertEqual(self.p.account.equity,D(100001))
