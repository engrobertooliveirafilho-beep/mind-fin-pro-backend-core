import unittest
from tests.test_et665_m8_gateway_e2e import M8GatewayE2E
from mind_trader.app.backtest.p2405_paper_gateway import replay_financially_verified_candidate
from mind_trader.app.risk.paper_financial_contract import verify_paper_financial_contract


class FinancialContractTests(unittest.TestCase):
    def check(self,side="BUY",entry_fill=100,stop=99,quantity=2,
              quote_to_account_rate=1,contract_multiplier=1,
              commission_per_unit_per_side=0.5,spread=0.2,slippage=0.1,
              reserved_risk_account=4.4):
        return verify_paper_financial_contract(
            side=side,entry_fill=entry_fill,stop=stop,quantity=quantity,
            quote_to_account_rate=quote_to_account_rate,
            contract_multiplier=contract_multiplier,
            commission_per_unit_per_side=commission_per_unit_per_side,
            spread=spread,slippage=slippage,
            reserved_risk_account=reserved_risk_account)

    def test_buy_exact_risk(self):
        r=self.check()
        self.assertEqual(r["decision"],"FINANCIAL_CONTRACT_VALIDATED",r)
        self.assertAlmostEqual(r["expected_stop_loss_account"],4.4)

    def test_sell_exact_risk(self):
        r=self.check(side="SELL",stop=101)
        self.assertEqual(r["decision"],"FINANCIAL_CONTRACT_VALIDATED",r)
        self.assertAlmostEqual(r["expected_stop_loss_account"],4.4)

    def test_under_reserved_risk_blocked(self):
        r=self.check(reserved_risk_account=4)
        self.assertEqual(r["reason"],"UNDER_RESERVED_STOP_LOSS")

    def test_quote_to_account_fx_conversion(self):
        r=self.check(quote_to_account_rate=2,reserved_risk_account=8.8)
        self.assertEqual(r["decision"],"FINANCIAL_CONTRACT_VALIDATED",r)
        self.assertAlmostEqual(r["expected_stop_loss_account"],8.8)

    def test_contract_multiplier(self):
        r=self.check(contract_multiplier=100,reserved_risk_account=440)
        self.assertEqual(r["decision"],"FINANCIAL_CONTRACT_VALIDATED",r)
        self.assertAlmostEqual(r["expected_stop_loss_account"],440)

    def test_adversarial_costs_block(self):
        r=self.check(slippage=1,reserved_risk_account=4.4)
        self.assertEqual(r["reason"],"UNDER_RESERVED_STOP_LOSS")

    def test_invalid_side_stop_or_units(self):
        self.assertEqual(self.check(side="HOLD")["reason"],"INVALID_SIDE")
        self.assertEqual(self.check(stop=101)["reason"],"INVALID_STOP_DIRECTION")
        self.assertEqual(self.check(quantity=0)["reason"],"INVALID_POSITIVE_UNITS")
        self.assertEqual(self.check(quote_to_account_rate=0)["reason"],"INVALID_POSITIVE_UNITS")
        self.assertEqual(self.check(commission_per_unit_per_side=-1)["reason"],"INVALID_COSTS")


class StrictFinancialReplayTests(M8GatewayE2E):
    def test_under_reserve_never_reaches_broker(self):
        result=replay_financially_verified_candidate(self.candidate,self.gateway,
            quantity=100,quote_to_account_rate=1,contract_multiplier=1,
            risk_amount=10,stop_distance=1,regime_report=self.regime,
            genome=self.genome,authorize_offline_replay=True)
        self.assertEqual(result["reason"],"UNDER_RESERVED_STOP_LOSS",result)
        self.assertFalse(self.broker.exists())

    def test_verified_replay_accepts_with_adequate_reserve(self):
        result=replay_financially_verified_candidate(self.candidate,self.gateway,
            quantity=1,quote_to_account_rate=1,contract_multiplier=1,
            risk_amount=10,stop_distance=1,regime_report=self.regime,
            genome=self.genome,authorize_offline_replay=True)
        self.assertEqual(result["decision"],"ACCEPT_SIMULATED_ORDER",result)
        self.assertEqual(result["financial_contract"]["decision"],"FINANCIAL_CONTRACT_VALIDATED")


if __name__=="__main__":
    unittest.main()
