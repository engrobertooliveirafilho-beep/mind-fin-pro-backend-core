"""ET-653: isolated PAPER end-to-end integration, never broker-connected."""
import unittest
from datetime import date
from mind_trader.ftmo_paper_execution import D,Rules,OrderIntent,PaperPortfolio,ExecutionV6
from mind_trader.ftmo_paper_execution.certification_gate_v7 import assess,REQUIRED
class E2E(unittest.TestCase):
    def setUp(self):
        self.p=PaperPortfolio(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))
        self.e=ExecutionV6(self.p)
    def order(self,qty=1):
        return OrderIntent('BUY',D(100),D(90),D(qty),D(1))
    def test_stop_first_and_gate_block(self):
        pid=self.p.open(self.order())
        self.assertIsNotNone(pid)
        result=self.e.process_bar({pid:{'open':100,'high':125,'low':85,'close':110,'target':120}})
        self.assertEqual(result['exits'],1)
        self.assertEqual(self.p.account.balance,D(99990))
        self.assertEqual(result['real_orders'],0)
        gate=assess({'end_to_end_integration_pass':True},paper_tests_pass=True)
        self.assertFalse(gate.release_authorized)
        self.assertEqual(len(gate.missing),len(REQUIRED)-1)
    def test_intrabar_breach_blocks_new_orders(self):
        pid=self.p.open(self.order(100))
        result=self.e.process_bar({pid:{'open':100,'high':105,'low':40,'close':100,'target':120}})
        self.assertTrue(result['intrabar_breach'])
        self.assertTrue(result['halted'])
        self.assertIsNone(self.p.open(self.order()))
        self.assertEqual(result['real_orders'],0)
    def test_gate_rejects_fabricated_evidence(self):
        with self.assertRaises(ValueError): assess({'invented':True},paper_tests_pass=True)
        with self.assertRaises(TypeError): assess({REQUIRED[0]:'PASS'},paper_tests_pass=True)
if __name__=='__main__':unittest.main()
