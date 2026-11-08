"""R90: regression witness for previously uncounted PAPER fills.

After R113, unconfigured capacity must block instead of issuing orders.
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
SESSION = EXEC / "paper_session.py"

def extract(path, name, namespace, class_name=None):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    nodes = tree.body if class_name is None else next(n.body for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    fn = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == name)
    body = [fn] if class_name is None else [ast.ClassDef(name=class_name, bases=[], keywords=[], body=[fn], decorator_list=[])]
    exec(compile(ast.fix_missing_locations(ast.Module(body=body, type_ignores=[])), str(path), "exec"), namespace)
    return namespace[name] if class_name is None else namespace[class_name]

class R90SessionAccountingGap(unittest.TestCase):
    def test_repeated_fills_without_capacity_gate_fail_closed(self):
        ns = {"json": json, "uuid": uuid, "datetime": datetime, "UTC": UTC,
              "Path": Path, "math": math,
              "ALLOWED_MODES": {"PAPER", "REPLAY", "MICRO_SIM"},
              "LIVE_MODE_TO_ACTION": {"FTMO_REAL": "FTMO_REAL_TRADE"},
              "TradeIntent": lambda **kw: SimpleNamespace(**kw),
              "audit_rule_application": lambda *args: {"decision": "ALLOW_FTMO_SIMULATION"},
              "require_defined_regime": lambda *args: (True, "OK")}
        for filename, name in [
            ("safe_broker_adapter.py", "validate_order_payload"),
            ("paper_fill_model.py", "simulate_fill"),
            ("paper_broker_adapter.py", "write_paper_broker_ledger"),
            ("paper_broker_adapter.py", "paper_route_order"),
        ]:
            extract(EXEC / filename, name, ns)
        extract(GATEWAY, "write_execution_ledger", ns)
        gateway_type = extract(GATEWAY, "submit_order", ns, "ExecutionGateway")
        session_methods = ["_read_session", "pre_trade_check"]
        tree = ast.parse(SESSION.read_text(encoding="utf-8"))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PaperTradingSessionManager")
        methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in session_methods]
        session_cls = ast.ClassDef(name="PaperTradingSessionManager", bases=[], keywords=[], body=methods, decorator_list=[])
        exec(compile(ast.fix_missing_locations(ast.Module(body=[session_cls], type_ignores=[])), str(SESSION), "exec"), ns)
        trade = {"symbol": "TEST", "side": "BUY", "strategy_id": "TEST",
                 "entry": 100.0, "stop": 95.0, "target": 110.0, "risk_amount": 1.0}
        with tempfile.TemporaryDirectory(prefix="et665_r90_") as tmp:
            session_path = Path(tmp) / "session.json"
            session_path.write_text(json.dumps({
                "session_id": "offline", "status": "OPEN", "trades": 0,
                "max_daily_trades": 1, "daily_pnl": 0.0, "max_daily_loss": 100.0,
                "loss_streak": 0, "ftmo_config_hash": "offline"
            }), encoding="utf-8")
            session = object.__new__(ns["PaperTradingSessionManager"])
            session.session_path = session_path
            session.ftmo_config_path = None
            gateway = object.__new__(gateway_type)
            gateway.ledger_path = str(Path(tmp) / "execution.jsonl")
            gateway.paper_broker_ledger_path = str(Path(tmp) / "broker.jsonl")
            gateway.paper = session
            gateway.ftmo = SimpleNamespace(validate=lambda *args: (True, "OK"))
            gateway.ftmo_config_valid = {"valid": True, "hash": "offline"}
            gateway.ftmo_ruleset = {"version": "offline"}
            gateway.risk = SimpleNamespace(validate=lambda *args: (True, "OK"))
            gateway.adv = SimpleNamespace(review_trade=lambda *args: {"adversarial_passed": True, "decision": "OK"})
            decisions = [gateway.submit_order("PAPER", trade, {"regime": "DEFINED"}, {"genome_id": "offline"})["decision"] for _ in range(2)]
            self.assertEqual(decisions, ["REJECT_ORDER", "REJECT_ORDER"])
            self.assertEqual(session._read_session()["trades"], 0)
            self.assertFalse(Path(gateway.paper_broker_ledger_path).exists())
            self.assertEqual(len(Path(gateway.ledger_path).read_text().splitlines()), 2)

if __name__ == "__main__":
    unittest.main()
