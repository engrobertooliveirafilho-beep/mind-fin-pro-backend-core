"""V5 PAPER chronological day-contract regressions."""
import unittest
from datetime import date, datetime
from app.runtime.ftmo_execution_v5 import ExecutionV5
from app.runtime.portfolio_runtime import PaperPortfolio
from app.runtime.ftmo_paper_guard import Rules, D

class V5DayContract(unittest.TestCase):
    def setUp(self):
        self.p = PaperPortfolio(Rules(D(100000), D(".05"), D(".10"), D(".10")), date(2026, 10, 29))
        self.e = ExecutionV5(self.p)

    def test_datetime_rejected_before_mutation(self):
        before = (self.p.account.day, len(self.p.audit))
        with self.assertRaises(ValueError):
            self.e.process_bar({}, day=datetime(2026, 10, 30))
        self.assertEqual((self.p.account.day, len(self.p.audit)), before)

    def test_date_rollover_allowed(self):
        self.e.process_bar({}, day=date(2026, 10, 30))
        self.assertEqual(self.p.account.day, date(2026, 10, 30))

    def test_string_rejected(self):
        with self.assertRaises(ValueError):
            self.e.process_bar({}, day="2026-10-30")
