"""Offline gateway regression and crash-window checks; no broker/network access."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from mind_trader.app.execution.gateway import ExecutionGateway
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class GatewaySafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        p=Path(self.temp.name)
        config=p/"ftmo.json"
        config.write_text(json.dumps(default_ftmo_config()),encoding="utf-8")
        self.gateway=ExecutionGateway(
            ledger_path=str(p/"execution.jsonl"),
            ftmo_config_path=str(config),
            paper_session_path=str(p/"session.json"),
            paper_day_ledger_path=str(p/"day.jsonl"),
            paper_broker_ledger_path=str(p/"broker.jsonl"))
        self.assertEqual(self.gateway.paper.open_session()["decision"],"SESSION_OPENED")
        self.order={"symbol":"EURUSD","strategy_id":"test","entry":1.10,"stop":1.09,"target":1.12,"risk_amount":100,"client_order_id":"test-001"}
    def tearDown(self):
        self.temp.cleanup()
    def test_real_modes_never_route(self):
        with patch("mind_trader.app.execution.gateway.paper_route_order",side_effect=AssertionError("broker called")):
            for mode in ("LIVE","PRODUCTION","REAL_MONEY","FTMO_REAL","BROKER"):
                with self.subTest(mode=mode):
                    result=self.gateway.submit_order(mode,self.order,{}, {})
                    self.assertNotEqual(result.get("decision"),"ACCEPT_SIMULATED_ORDER")
                    self.assertEqual(result.get("production"),"BLOCKED")
    def test_missing_id_blocks_before_broker(self):
        order=dict(self.order)
        del order["client_order_id"]
        with patch("mind_trader.app.execution.gateway.paper_route_order",side_effect=AssertionError("broker called")):
            result=self.gateway.submit_order("PAPER",order,{}, {})
        self.assertEqual(result["decision"],"BLOCKED_MISSING_ORDER_FIELDS")
    def test_unsettled_fill_blocks_gateway(self):
        reservation=self.gateway.paper.reserve_paper_order(100,"pending-intent")
        broker=Path(self.gateway.paper_broker_ledger_path)
        broker.write_text(json.dumps({"decision":"PAPER_ORDER_ACCEPTED","order":{"reservation_id":reservation["reservation_id"]},"fill":{"filled":True}})+"\n")
        with patch("mind_trader.app.execution.gateway.paper_route_order",side_effect=AssertionError("broker called")):
            result=self.gateway.submit_order("PAPER",self.order,{}, {})
        self.assertEqual(result["decision"],"BLOCKED_PAPER_RECONCILIATION")
        self.assertEqual(result["reconciliation"]["decision"],"BLOCK_UNSETTLED_BROKER_FILL")
    def test_corrupt_broker_ledger_blocks_gateway(self):
        Path(self.gateway.paper_broker_ledger_path).write_text("{invalid")
        with patch("mind_trader.app.execution.gateway.paper_route_order",side_effect=AssertionError("broker called")):
            result=self.gateway.submit_order("PAPER",self.order,{}, {})
        self.assertEqual(result["decision"],"BLOCKED_PAPER_RECONCILIATION")
    def test_rejected_reservation_does_not_route(self):
        self.gateway.paper.reserve_paper_order(100,self.order["client_order_id"])
        with patch("mind_trader.app.execution.gateway.paper_route_order",side_effect=AssertionError("broker called")):
            result=self.gateway.submit_order("PAPER",self.order,{}, {})
        self.assertNotEqual(result["decision"],"ACCEPT_SIMULATED_ORDER")

if __name__=="__main__":
    unittest.main()
