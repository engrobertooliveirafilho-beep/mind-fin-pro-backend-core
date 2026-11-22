"""Direct FTMO PAPER account day rollover regression."""
import unittest
from datetime import date, datetime
from app.runtime.ftmo_paper_guard import D, Rules, PaperAccount

class AccountDayContract(unittest.TestCase):
    def setUp(self):
        self.a=PaperAccount.create(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))

    def test_datetime_rejected_without_mutation(self):
        before=(self.a.day,self.a.day_start_balance,self.a.day_start_equity,self.a.halted)
        with self.assertRaises(ValueError):
            self.a.new_day(datetime(2026,10,30))
        self.assertEqual((self.a.day,self.a.day_start_balance,self.a.day_start_equity,self.a.halted),before)

    def test_old_day_rejected(self):
        with self.assertRaises(ValueError):
            self.a.new_day(date(2026,10,28))

    def test_valid_day(self):
        self.a.new_day(date(2026,10,30))
        self.assertEqual(self.a.day,date(2026,10,30))
