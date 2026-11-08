"""R77: isolated execution of the actual gateway method with stubbed dependencies.

Never imports trader modules, broker, MetaTrader5 or network libraries.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[3]
GATEWAY = ROOT / "products/eldora_trader/mind_trader/app/execution/gateway.py"

class GatewayPaperContract(unittest.TestCase):
    def test_paper_broker_outcomes(self):
        tree = ast.parse(GATEWAY.read_text(encoding="utf-8"))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ExecutionGateway")
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "submit_order")
        isolated = ast.Module(body=[ast.ClassDef(name="ExecutionGateway", bases=[], keywords=[], body=[method], decorator_list=[])], type_ignores=[])
        ast.fix_missing_locations(isolated)

        def trade_intent(**kwargs):
            return SimpleNamespace(**kwargs)
        def ledger(event, path):
            return event
        for broker_response, expected in [
            ({"decision": "PAPER_ORDER_REJECTED_FILL", "fill": {"filled": False}}, "REJECT_ORDER"),
            ({"decision": "PAPER_ORDER_ACCEPTED", "fill": {"filled": False}}, "REJECT_ORDER"),
            ({"decision": "PAPER_ORDER_ACCEPTED", "fill": {}}, "REJECT_ORDER"),
            ({"decision": "PAPER_ORDER_ACCEPTED", "fill": {"filled": 1}}, "REJECT_ORDER"),
            ({"decision": "PAPER_ORDER_ACCEPTED", "fill": {"filled": True}}, "ACCEPT_SIMULATED_ORDER"),
            (None, "REJECT_ORDER"),
        ]:
            with self.subTest(response=broker_response):
                namespace = {
                    "ALLOWED_MODES": {"PAPER", "REPLAY", "MICRO_SIM"},
                    "LIVE_MODE_TO_ACTION": {},
                    "write_execution_ledger": ledger,
                    "TradeIntent": trade_intent,
                    "audit_rule_application": lambda *args: {"decision": "ALLOW_FTMO_SIMULATION"},
                    "require_defined_regime": lambda *args: (True, "OK"),
                    "paper_route_order": lambda *args, **kwargs: broker_response,
                }
                exec(compile(isolated, str(GATEWAY), "exec"), namespace)
                obj = object.__new__(namespace["ExecutionGateway"])
                obj.ledger_path = "unused"
                obj.paper_broker_ledger_path = "unused"
                obj.paper = SimpleNamespace(pre_trade_check=lambda *args: {"allowed": True, "decision": "ALLOW"}, ftmo_config_path="unused")
                obj.ftmo = SimpleNamespace(validate=lambda *args: (True, "OK"))
                obj.ftmo_config_valid = {"valid": True, "hash": "offline"}
                obj.ftmo_ruleset = {"version": "offline"}
                obj.risk = SimpleNamespace(validate=lambda *args: (True, "OK"))
                obj.adv = SimpleNamespace(review_trade=lambda *args: {"adversarial_passed": True, "decision": "OK"})
                result = obj.submit_order("PAPER", {"symbol": "TEST", "strategy_id": "TEST", "entry": 100.0, "target": 110.0, "risk_amount": 1.0}, {"regime": "DEFINED"}, {"genome_id": "offline"})
                self.assertEqual(result["decision"], expected)
                self.assertEqual(result["production"], "BLOCKED")
                self.assertEqual(result["real_broker_routing"], "DISABLED")

if __name__ == "__main__":
    unittest.main()
