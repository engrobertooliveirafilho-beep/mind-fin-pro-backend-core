"""R82: actual PAPER broker and fill functions, extracted without importing trading modules."""
import ast
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
BROKER = ROOT / "mind_trader/app/execution/paper_broker_adapter.py"
FILL = ROOT / "mind_trader/app/execution/paper_fill_model.py"

def isolate(path, function, env):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    exec(compile(module, str(path), "exec"), env)
    return env[function]

class R82PaperBrokerOffline(unittest.TestCase):
    def test_real_fill_and_broker_contract(self):
        events = []
        env = {"math": math, "validate_order_payload": lambda order: {"valid": isinstance(order, dict) and order.get("symbol") == "TEST"},
               "write_paper_broker_ledger": lambda event, path: events.append(dict(event)) or event}
        env["simulate_fill"] = isolate(FILL, "simulate_fill", env)
        broker = isolate(BROKER, "paper_route_order", env)
        order = {"symbol": "TEST", "side": "BUY", "entry": 100.0, "stop": 95.0,
                 "target": 110.0, "risk_amount": 1.0, "strategy_id": "TEST"}
        cases = [
            (order, 0.0, "PAPER_ORDER_ACCEPTED", True),
            (order, 0.2, "PAPER_ORDER_ACCEPTED", True),
            ({**order, "stop": None}, 0.0, "PAPER_ORDER_REJECTED_FILL", False),
            ({**order, "side": "INVALID"}, 0.0, "PAPER_ORDER_REJECTED_FILL", False),
            ({**order, "entry": float("nan")}, 0.0, "PAPER_ORDER_REJECTED_FILL", False),
            (order, -1.0, "PAPER_ORDER_REJECTED_FILL", False),
            ({**order, "symbol": "INVALID"}, 0.0, "PAPER_ORDER_REJECTED_INVALID_PAYLOAD", False),
        ]
        for payload, spread, expected, filled in cases:
            with self.subTest(expected=expected, payload=payload, spread=spread):
                result = broker(payload, spread=spread, ledger_path="memory-only")
                self.assertEqual(result["decision"], expected)
                self.assertEqual(result["production"], "BLOCKED")
                self.assertEqual(result["live"], "FORBIDDEN")
                if expected == "PAPER_ORDER_ACCEPTED":
                    self.assertIs(result["fill"]["filled"], filled)
                    self.assertEqual(result["real_broker_routing"], "DISABLED")
                self.assertEqual(events[-1], result)

if __name__ == "__main__":
    unittest.main()
