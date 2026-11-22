"""PAPER trade numeric inputs must be validated before balance mutation."""
import unittest
from datetime import date
from app.runtime.ftmo_paper_guard import D, Rules, PaperAccount

class PaperNumericAtomicity(unittest.TestCase):
    def setUp(self):
        self.a = PaperAccount.create(Rules(D(100000),D('.05'),D('.10'),D('.10')),date(2026,10,29))

    def test_nan_exit_cannot_corrupt_balance(self):
        before=(self.a.balance,self.a.equity,self.a.trades)
        with self.assertRaises(ValueError): self.a.close_paper_trade('BUY',100,'NaN',1,1)
        self.assertEqual((self.a.balance,self.a.equity,self.a.trades),before)
        self.assertEqual(self.a.status()['real_orders'],0)

    def test_infinite_commission_rejected(self):
        before=(self.a.balance,self.a.equity,self.a.trades)
        with self.assertRaises(ValueError): self.a.close_paper_trade('SELL',100,99,1,1,commission='Infinity')
        self.assertEqual((self.a.balance,self.a.equity,self.a.trades),before)

    def test_valid_paper_trade_preserved(self):
        self.assertEqual(self.a.close_paper_trade('BUY',100,102,2,1,commission=1,slippage_cost=1),D(2))
        self.assertEqual(self.a.balance,D(100002))
        self.assertEqual(self.a.trades,1)
