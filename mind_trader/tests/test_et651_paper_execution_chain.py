"""ET-651 regression of isolated PAPER V6 -> V5 -> V4 and V2/V3 dependencies."""
import unittest
from datetime import date
from mind_trader.ftmo_paper_execution import D,Rules,OrderIntent,PaperPortfolio,ExecutionV6
class TestPaperExecutionChain(unittest.TestCase):
    def setUp(self):
        self.p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        self.e=ExecutionV6(self.p)
    def order(self,side='BUY',qty=1):
        return OrderIntent(side,D(100),D(90 if side=='BUY' else 110),D(qty),D(1))
    def test_valid_bar_no_real_orders(self):
        pid=self.p.open(self.order())
        result=self.e.process_bar({pid:{'open':100,'high':102,'low':99,'close':101,'target':120}})
        self.assertFalse(result['halted'])
        self.assertFalse(result['intrabar_breach'])
        self.assertEqual(result['real_orders'],0)
    def test_intrabar_halt_even_after_recovery(self):
        pid=self.p.open(self.order(qty=100))
        result=self.e.process_bar({pid:{'open':100,'high':105,'low':40,'close':100,'target':120}})
        self.assertTrue(result['halted'])
        self.assertTrue(result['intrabar_breach'])
        self.assertIsNone(self.p.open(self.order()))
    def test_breach_flag_is_current_bar_only(self):
        pid=self.p.open(self.order(qty=100))
        self.assertTrue(self.e.process_bar({pid:{'open':100,'high':105,'low':40,'close':100,'target':120}})['intrabar_breach'])
        self.assertFalse(self.e.process_bar({})['intrabar_breach'])
        self.assertTrue(self.p.account.halted)
    def test_invalid_bar_does_not_roll_day(self):
        pid=self.p.open(self.order())
        with self.assertRaises(ValueError):
            self.e.process_bar({pid:{'open':100,'high':99,'low':101,'close':100,'target':120}},day=date(2026,10,30))
        self.assertEqual(self.p.account.day,date(2026,10,29))
    def test_missing_bar_does_not_roll_day(self):
        self.p.open(self.order())
        with self.assertRaises(ValueError): self.e.process_bar({},day=date(2026,10,30))
        self.assertEqual(self.p.account.day,date(2026,10,29))
    def test_stop_precedes_target(self):
        pid=self.p.open(self.order())
        r=self.e.process_bar({pid:{'open':100,'high':125,'low':85,'close':110,'target':120}})
        self.assertEqual(r['exits'],1)
        self.assertEqual(self.p.account.balance,D(99990))
        self.assertEqual(r['real_orders'],0)
    def test_rollover(self):
        pid=self.p.open(self.order())
        self.e.process_bar({pid:{'open':100,'high':102,'low':99,'close':100,'target':120}},day=date(2026,10,30))
        self.assertEqual(self.p.account.day,date(2026,10,30))
if __name__=='__main__': unittest.main()
