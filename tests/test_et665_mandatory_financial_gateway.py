"""Fail-closed migration checks for mandatory PAPER financial units."""
import json
import tests.test_et665_m8_gateway_e2e as m8fixture
from mind_trader.app.backtest.p2405_paper_gateway import (
    replay_candidate_to_paper,replay_financially_verified_candidate)
from mind_trader.app.backtest.p2405_paper_settlement import settle_historical_paper_exit


import unittest

class MandatoryFinancialGatewayTests(unittest.TestCase):
    def setUp(self):
        m8fixture.M8GatewayE2E.setUp(self)
    def test_legacy_replay_without_units_blocked(self):
        result=replay_candidate_to_paper(self.candidate,self.gateway,
            risk_amount=10,stop_distance=1,regime_report=self.regime,
            genome=self.genome,authorize_offline_replay=True)
        self.assertEqual(result["decision"],"BLOCKED_MISSING_FINANCIAL_CONTRACT")
        self.assertFalse(self.broker.exists())

    def test_strict_replay_persists_units_and_rejects_quantity_drift(self):
        result=replay_financially_verified_candidate(self.candidate,self.gateway,
            quantity=1,quote_to_account_rate=1,contract_multiplier=1,
            risk_amount=10,stop_distance=1,regime_report=self.regime,
            genome=self.genome,authorize_offline_replay=True)
        self.assertEqual(result["decision"],"ACCEPT_SIMULATED_ORDER",result)
        broker=json.loads(self.broker.read_text().splitlines()[0])
        self.assertEqual(broker["order"]["quantity"],1)
        self.assertEqual(broker["order"]["quote_to_account_rate"],1)
        self.assertEqual(broker["order"]["contract_multiplier"],1)
        rejected=settle_historical_paper_exit(self.manager,
            broker_ledger_path=str(self.broker),reservation_id=result["reservation_id"],
            entry_ts=self.candidate["fill_ts"],exit_ts="2026-01-03T00:00:00",
            exit_close=102,quantity=2,quote_to_account_rate=1,
            settlement_evidence_path=str(self.root/"bad_settlement.json"),
            authorize_offline_replay=True)
        self.assertEqual(rejected["reason"],"SETTLEMENT_QUANTITY_MISMATCH")
        self.assertEqual(json.loads(self.session.read_text())["trades"],0)
        self.assertFalse((self.root/"bad_settlement.json").exists())

    def test_settlement_fx_mismatch_rejected(self):
        result=replay_financially_verified_candidate(self.candidate,self.gateway,
            quantity=1,quote_to_account_rate=1,contract_multiplier=1,
            risk_amount=10,stop_distance=1,regime_report=self.regime,
            genome=self.genome,authorize_offline_replay=True)
        self.assertEqual(result["decision"],"ACCEPT_SIMULATED_ORDER",result)
        rejected=settle_historical_paper_exit(self.manager,
            broker_ledger_path=str(self.broker),reservation_id=result["reservation_id"],
            entry_ts=self.candidate["fill_ts"],exit_ts="2026-01-03T00:00:00",
            exit_close=102,quantity=1,quote_to_account_rate=2,
            settlement_evidence_path=str(self.root/"bad_fx.json"),
            authorize_offline_replay=True)
        self.assertEqual(rejected["reason"],"SETTLEMENT_FX_MISMATCH")
        self.assertEqual(json.loads(self.session.read_text())["trades"],0)
