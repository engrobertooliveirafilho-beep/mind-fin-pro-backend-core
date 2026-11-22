"""Offline PAPER V6-to-V7 integration regression; no broker connectivity."""
import unittest
from datetime import date
from app.runtime.ftmo_paper_guard import D, Rules
from app.runtime.ftmo_pretrade_v2 import OrderIntent
from app.runtime.portfolio_runtime import PaperPortfolio
from app.runtime.ftmo_execution_v6 import ExecutionV6
from app.runtime.certification_gate_v7 import REQUIRED, assess

class WiringTests(unittest.TestCase):
    def setUp(self):
        self.p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        self.e=ExecutionV6(self.p)

    def test_paper_success_does_not_unlock_evidence_gate(self):
        pid=self.p.open(OrderIntent('BUY',D(100),D(95),D(1),D(1)))
        result=self.e.process_bar({pid:dict(open=100,high=102,low=99,close=101,target=120)})
        self.assertFalse(result['halted'])
        self.assertEqual(result['real_orders'],0)
        gate=assess({},paper_tests_pass=True)
        self.assertTrue(gate.paper_technical_tests)
        self.assertFalse(gate.release_authorized)
        self.assertEqual(len(gate.missing),len(REQUIRED))

    def test_intrabar_halt_cannot_be_overridden_by_gate(self):
        pid=self.p.open(OrderIntent('BUY',D(100),D(90),D(1),D(100)))
        result=self.e.process_bar({pid:dict(open=100,high=105,low=40,close=100,target=120)})
        self.assertTrue(result['halted'])
        gate=assess({},paper_tests_pass=False)
        self.assertFalse(gate.release_authorized)
        self.assertEqual(result['real_orders']+gate.real_orders,0)

    def test_invalid_bar_rejected_without_gate_progress(self):
        pid=self.p.open(OrderIntent('BUY',D(100),D(90),D(1),D(100)))
        before=(self.p.account.day,len(self.p.audit))
        with self.assertRaises(ValueError):
            self.e.process_bar({pid:dict(open=100,high=90,low=101,close=100,target=120)},day=date(2026,10,30))
        self.assertEqual((self.p.account.day,len(self.p.audit)),before)
        self.assertFalse(assess({},paper_tests_pass=False).release_authorized)

    def test_gate_rejects_untyped_test_result(self):
        with self.assertRaises(TypeError):
            assess(dict.fromkeys(REQUIRED,True),paper_tests_pass='PASS')
