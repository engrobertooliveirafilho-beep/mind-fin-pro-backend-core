import unittest
from datetime import date
from decimal import Decimal
from app.runtime.p2614_real_fill_replay.ftmo_paper_guard import Rules,D
from app.runtime.p2614_real_fill_replay.ftmo_pretrade_v2 import OrderIntent
from app.runtime.p2614_real_fill_replay.portfolio_runtime import PaperPortfolio
from app.runtime.p2614_real_fill_replay.ftmo_execution_v6 import ExecutionV6

class TestV6(unittest.TestCase):
    def setUp(self):
        self.p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        self.e=ExecutionV6(self.p)
    def order(self,side='BUY'):
        return OrderIntent(side,D(100),D(90 if side=='BUY' else 110),D(1),D(100))
    def test_intrabar_breach_even_when_close_recovers(self):
        pid=self.p.open(self.order());self.assertIsNotNone(pid)
        result=self.e.process_bar({pid:{'open':100,'high':105,'low':40,'close':100,'target':120}})
        self.assertTrue(result['halted']);self.assertTrue(result['intrabar_breach'])
    def test_normal_bar(self):
        pid=self.p.open(self.order());r=self.e.process_bar({pid:{'open':100,'high':102,'low':99,'close':101,'target':120}})
        self.assertFalse(r['halted']);self.assertFalse(r['intrabar_breach'])
    def test_invalid_bar_no_mutation(self):
        pid=self.p.open(self.order());before=self.p.snapshot()
        with self.assertRaises(ValueError):self.e.process_bar({pid:{'open':100,'high':99,'low':101,'close':100,'target':120}},day=date(2026,10,30))
        self.assertEqual(self.p.account.day,date(2026,10,29));self.assertEqual(self.p.snapshot()['account'],before['account'])
    def test_short_intrabar_breach(self):
        pid=self.p.open(self.order('SELL'));r=self.e.process_bar({pid:{'open':100,'high':160,'low':99,'close':100,'target':80}})
        self.assertTrue(r['halted'])
    def test_day_rollover(self):
        pid=self.p.open(self.order());self.e.process_bar({pid:{'open':100,'high':102,'low':99,'close':100,'target':120}},day=date(2026,10,30))
        self.assertEqual(self.p.account.day,date(2026,10,30))
if __name__=='__main__':unittest.main()
