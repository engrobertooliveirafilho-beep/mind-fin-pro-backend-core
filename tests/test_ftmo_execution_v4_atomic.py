"""ET-019 adversarial regression for recovered FTMO V4 PAPER engine.

Requires original Drive dependencies: ftmo_paper_guard.py, ftmo_pretrade_v2.py,
portfolio_runtime.py on PYTHONPATH. Tests run offline in isolated staging.
"""
import unittest
from datetime import date
from ftmo_paper_guard import D, Rules
from ftmo_pretrade_v2 import OrderIntent
from portfolio_runtime import PaperPortfolio
from app.runtime.ftmo_execution_v4 import ExecutionV4

class AtomicBarTests(unittest.TestCase):
    def test_marks_complete_bar_before_first_close(self):
        p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        ids=[p.open(OrderIntent('BUY',D(100),D(95),D(1),D(1))) for _ in range(3)]
        def bar(hi,lo,cl,tp):return dict(open=100,high=hi,low=lo,close=cl,target=tp)
        result=ExecutionV4(p).process_bar({ids[0]:bar(111,99,108,110),ids[1]:bar(104,94,96,110),ids[2]:bar(105,99,104,110)})
        self.assertEqual(result['exits'],2)
        self.assertEqual(p.account.equity,D(100009))
        events=[x['event'] for x in p.audit]
        self.assertLess(events.index('MARK'),events.index('CLOSE'))
        self.assertEqual(result['real_orders'],0)

    def test_reject_invalid_input_without_mutation(self):
        p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        k=p.open(OrderIntent('BUY',D(100),D(95),D(1),D(1)))
        before=(p.account.balance,p.account.equity,len(p.audit))
        with self.assertRaises(ValueError):
            ExecutionV4(p).process_bar({k:dict(open=100,high=90,low=110,close=100,target=110)})
        self.assertEqual((p.account.balance,p.account.equity,len(p.audit)),before)
