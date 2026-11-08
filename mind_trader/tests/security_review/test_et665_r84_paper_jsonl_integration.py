"""R84: real PAPER validation -> fill -> broker -> JSONL ledger, offline only.

Extract original functions by AST to prevent module-level imports/side effects.
No trading connectivity; temporary ledger file only.
"""
import ast
from datetime import datetime, UTC
import json
import math
from pathlib import Path
import tempfile
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[3]
EXEC = ROOT / "mind_trader/app/execution"

def load_function(path, name, namespace):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    code = compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(path), "exec")
    exec(code, namespace)
    return namespace[name]

class R84PaperIntegratedOffline(unittest.TestCase):
    def test_actual_broker_validation_fill_and_jsonl(self):
        ns = {"json": json, "uuid": uuid, "datetime": datetime, "UTC": UTC,
              "Path": Path, "math": math}
        for filename, name in [
            ("safe_broker_adapter.py", "validate_order_payload"),
            ("paper_fill_model.py", "simulate_fill"),
            ("paper_broker_adapter.py", "write_paper_broker_ledger"),
            ("paper_broker_adapter.py", "paper_route_order"),
            ("paper_broker_adapter.py", "paper_broker_summary"),
        ]:
            load_function(EXEC / filename, name, ns)
        order = {"symbol": "TEST", "side": "BUY", "entry": 100.0, "stop": 95.0,
                 "target": 110.0, "risk_amount": 1.0, "strategy_id": "TEST"}
        with tempfile.TemporaryDirectory(prefix="et665_r84_") as temp:
            ledger = str(Path(temp) / "paper.jsonl")
            cases = [
                (order, "PAPER_ORDER_ACCEPTED"),
                ({**order, "entry": float("nan")}, "PAPER_ORDER_REJECTED_FILL"),
                ({**order, "side": "INVALID"}, "PAPER_ORDER_REJECTED_FILL"),
                ({**order, "stop": None}, "PAPER_ORDER_REJECTED_INVALID_PAYLOAD"),
                ({**order, "symbol": ""}, "PAPER_ORDER_REJECTED_INVALID_PAYLOAD"),
            ]
            for payload, expected in cases:
                with self.subTest(expected=expected, payload=payload):
                    result = ns["paper_route_order"](payload, ledger_path=ledger)
                    self.assertEqual(result["decision"], expected)
                    self.assertEqual(result["production"], "BLOCKED")
                    self.assertEqual(result["live"], "FORBIDDEN")
                    self.assertTrue(result["paper_order_id"])
                    self.assertTrue(result["ts"])
                    if expected == "PAPER_ORDER_ACCEPTED":
                        self.assertIs(result["fill"]["filled"], True)
                        self.assertEqual(result["real_broker_routing"], "DISABLED")
            records = [json.loads(line) for line in Path(ledger).read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), len(cases))
            self.assertEqual([r["decision"] for r in records], [e for _, e in cases])
            summary = ns["paper_broker_summary"](ledger)
            self.assertEqual(summary["orders"], 5)
            self.assertEqual(summary["accepted"], 1)
            self.assertEqual(summary["rejected"], 4)

if __name__ == "__main__":
    unittest.main()
