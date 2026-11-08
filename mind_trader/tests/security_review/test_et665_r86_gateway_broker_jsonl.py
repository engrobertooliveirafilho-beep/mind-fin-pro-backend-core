"""R86: gateway -> real PAPER broker -> fill -> both JSONL ledgers offline.

AST extraction avoids importing trading modules or opening broker/network connections.
Risk, FTMO and session approval remain explicit stubs: not full E2E certification.
"""
import ast
from datetime import datetime, UTC
import json
import math
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[3]
EXEC = ROOT / "mind_trader/app/execution"
GATEWAY = ROOT / "products/eldora_trader/mind_trader/app/execution/gateway.py"

def extract(path, name, namespace, class_name=None):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    nodes = tree.body if class_name is None else next(n.body for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    fn = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == name)
    body = [fn] if class_name is None else [ast.ClassDef(name=class_name, bases=[], keywords=[], body=[fn], decorator_list=[])]
    exec(compile(ast.fix_missing_locations(ast.Module(body=body, type_ignores=[])), str(path), "exec"), namespace)
    return namespace[name] if class_name is None else namespace[class_name]

class R86GatewayBrokerJsonl(unittest.TestCase):
    def test_gateway_through_real_broker_and_persisted_ledgers(self):
        ns = {"json": json, "uuid": uuid, "datetime": datetime, "UTC": UTC,
              "Path": Path, "math": math,
              "ALLOWED_MODES": {"PAPER", "REPLAY", "MICRO_SIM"},
              "LIVE_MODE_TO_ACTION": {"LIVE": "LIVE_TRADE", "FTMO_REAL": "FTMO_REAL_TRADE"},
              "TradeIntent": lambda **kwargs: SimpleNamespace(**kwargs),
              "audit_rule_application": lambda *args: {"decision": "ALLOW_FTMO_SIMULATION"},
              "require_defined_regime": lambda *args: (True, "OK"),
              "institutional_live_lock": lambda *args: {"decision": "FORCE_BLOCK_LIVE"}}
        for filename, name in [
            ("safe_broker_adapter.py", "validate_order_payload"),
            ("paper_fill_model.py", "simulate_fill"),
            ("paper_broker_adapter.py", "write_paper_broker_ledger"),
            ("paper_broker_adapter.py", "paper_route_order"),
        ]:
            extract(EXEC / filename, name, ns)
        extract(GATEWAY, "write_execution_ledger", ns)
        gateway_type = extract(GATEWAY, "submit_order", ns, "ExecutionGateway")
        trade = {"symbol": "TEST", "side": "BUY", "strategy_id": "TEST", "entry": 100.0,
                 "stop": 95.0, "target": 110.0, "risk_amount": 1.0}
        with tempfile.TemporaryDirectory(prefix="et665_r86_") as temp:
            obj = object.__new__(gateway_type)
            obj.ledger_path = str(Path(temp) / "execution.jsonl")
            obj.paper_broker_ledger_path = str(Path(temp) / "broker.jsonl")
            obj.paper = SimpleNamespace(pre_trade_check=lambda *args: {"allowed": True, "decision": "ALLOW", "session_id": "offline"},
                                        ftmo_config_path=None)
            class InMemoryCapacity:
                def reserve_new(self, session_id, limit):
                    return {"decision":"RESERVED","order_id":str(uuid.uuid4())}
                def finalize(self, session_id, order_id, filled):
                    return "FILLED" if filled is True else "REJECTED"
            obj.paper_capacity = InMemoryCapacity()
            obj.paper_capacity_max_daily_trades = 2
            obj.ftmo = SimpleNamespace(validate=lambda *args: (True, "OK"))
            obj.ftmo_config_valid = {"valid": True, "hash": "offline"}
            obj.ftmo_ruleset = {"version": "offline"}
            obj.risk = SimpleNamespace(validate=lambda *args: (True, "OK"))
            obj.adv = SimpleNamespace(review_trade=lambda *args: {"adversarial_passed": True, "decision": "OK"})
            results = [
                obj.submit_order("PAPER", trade, {"regime": "DEFINED"}, {"genome_id": "offline"}),
                obj.submit_order("PAPER", {**trade, "stop": None}, {"regime": "DEFINED"}, {"genome_id": "offline"}),
                obj.submit_order("FTMO_REAL", trade, {"regime": "DEFINED"}, {"genome_id": "offline"}),
            ]
            self.assertEqual([r["decision"] for r in results],
                             ["ACCEPT_SIMULATED_ORDER", "REJECT_ORDER", "FORCE_BLOCK_LIVE"])
            self.assertTrue(all(r["production"] == "BLOCKED" for r in results))
            self.assertEqual([r["real_broker_routing"] for r in results[:2]], ["DISABLED", "DISABLED"])
            execution = [json.loads(x) for x in Path(obj.ledger_path).read_text().splitlines()]
            broker = [json.loads(x) for x in Path(obj.paper_broker_ledger_path).read_text().splitlines()]
            self.assertEqual(len(execution), 3)
            self.assertEqual([x["decision"] for x in broker], ["PAPER_ORDER_ACCEPTED", "PAPER_ORDER_REJECTED_INVALID_PAYLOAD"])
            self.assertEqual(execution[0]["paper_broker"]["paper_order_id"], broker[0]["paper_order_id"])
            self.assertEqual(execution[1]["paper_broker"]["paper_order_id"], broker[1]["paper_order_id"])

if __name__ == "__main__":
    unittest.main()
