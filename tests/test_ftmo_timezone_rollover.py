"""PAPER account-local IANA day rollover regression; timezone is explicit, not an FTMO policy claim."""
import unittest
from datetime import date, datetime, timezone
from app.runtime.ftmo_paper_guard import D, Rules, PaperAccount

class TimezoneRollover(unittest.TestCase):
    def setUp(self):
        self.a=PaperAccount.create(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))

    def test_local_midnight_boundary(self):
        self.assertFalse(self.a.rollover_at(datetime(2026,10,29,22,59,tzinfo=timezone.utc),'Europe/Prague'))
        self.assertEqual(self.a.day,date(2026,10,29))
        self.assertTrue(self.a.rollover_at(datetime(2026,10,29,23,0,tzinfo=timezone.utc),'Europe/Prague'))
        self.assertEqual(self.a.day,date(2026,10,30))

    def test_naive_rejected_no_mutation(self):
        before=(self.a.day,self.a.equity)
        with self.assertRaises(ValueError):
            self.a.rollover_at(datetime(2026,10,30),'Europe/Prague')
        self.assertEqual((self.a.day,self.a.equity),before)

    def test_invalid_zone_rejected(self):
        with self.assertRaises(ValueError):
            self.a.rollover_at(datetime(2026,10,30,tzinfo=timezone.utc),'Invalid/Zone')

    def test_earlier_day_rejected(self):
        with self.assertRaises(ValueError):
            self.a.rollover_at(datetime(2026,10,28,tzinfo=timezone.utc),'UTC')
