"""ET665.R119: structural interlock regressions; no real MT5/broker calls."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GATEWAY = ROOT / "products/eldora_trader/mind_trader/app/execution/gateway.py"
SESSION = ROOT / "products/eldora_trader/mind_trader/app/execution/paper_session.py"


def test_gateway_has_no_mt5_or_subprocess_imports():
    tree = ast.parse(GATEWAY.read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not any(name == "MetaTrader5" or name.startswith("MetaTrader5.")
                   or name == "subprocess" or name.startswith("subprocess.")
                   for name in imported)


def test_gateway_preserves_explicit_live_lock():
    tree = ast.parse(GATEWAY.read_text(encoding="utf-8"))
    source = GATEWAY.read_text(encoding="utf-8")
    assert '"FTMO_REAL":"FTMO_REAL_TRADE"' in source
    assert 'institutional_live_lock(' in source
    assert '"real_broker_routing":"DISABLED"' in source
    assert '"production":"BLOCKED"' in source
    assert any(isinstance(n, ast.FunctionDef) and n.name == "submit_order" for n in ast.walk(tree))


def test_session_result_not_claimed_as_atomic_with_capacity():
    source = SESSION.read_text(encoding="utf-8")
    # Documented open blocker: JSON session accounting is independent of SQLite reservations.
    assert "def record_trade_result(" in source
    assert "capacity_order_id" not in source
    assert "BEGIN IMMEDIATE" not in source


def test_gateway_validates_broker_receipt_session_and_capacity_id():
    source = GATEWAY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    submit = next(node for node in ast.walk(tree)
                  if isinstance(node, ast.FunctionDef) and node.name == "submit_order")
    checks = [node for node in ast.walk(submit) if isinstance(node, ast.Compare)]
    def is_mismatch(node, field, expected):
        return (isinstance(node.left, ast.Call) and isinstance(node.left.func, ast.Attribute)
                and node.left.func.attr == "get"
                and node.left.args and isinstance(node.left.args[0], ast.Constant)
                and node.left.args[0].value == field
                and any(isinstance(op, ast.NotEq) for op in node.ops)
                and any(isinstance(v, ast.Name) and v.id == expected for v in node.comparators))
    assert any(is_mismatch(node, "session_id", "session_id") for node in checks)
    assert any(is_mismatch(node, "capacity_order_id", "capacity_order_id") for node in checks)


def test_gateway_rejects_broker_live_routing_claims():
    tree = ast.parse(GATEWAY.read_text(encoding="utf-8"))
    submit = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "submit_order")
    comparisons = [n for n in ast.walk(submit) if isinstance(n, ast.Compare)]
    for field in ("real_broker_routing", "production", "mode"):
        assert any(isinstance(n.left, ast.Call)
                   and isinstance(n.left.func, ast.Attribute)
                   and n.left.func.attr == "get"
                   and n.left.args and isinstance(n.left.args[0], ast.Constant)
                   and n.left.args[0].value == field
                   and any(isinstance(op, ast.NotIn) for op in n.ops)
                   for n in comparisons)


def test_gateway_requires_internal_paper_broker_and_forbidden_live():
    tree = ast.parse(GATEWAY.read_text(encoding="utf-8"))
    submit = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "submit_order")
    comparisons = [n for n in ast.walk(submit) if isinstance(n, ast.Compare)]
    for field, expected in (("broker", "PAPER_INTERNAL"), ("live", "FORBIDDEN")):
        assert any(isinstance(n.left, ast.Call)
                   and isinstance(n.left.func, ast.Attribute)
                   and n.left.func.attr == "get"
                   and n.left.args and isinstance(n.left.args[0], ast.Constant)
                   and n.left.args[0].value == field
                   and any(isinstance(op, ast.NotEq) for op in n.ops)
                   and any(isinstance(v, ast.Constant) and v.value == expected for v in n.comparators)
                   for n in comparisons)


def test_gateway_requires_explicit_broker_production_and_routing_lock():
    tree = ast.parse(GATEWAY.read_text(encoding="utf-8"))
    submit = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "submit_order")
    comparisons = [n for n in ast.walk(submit) if isinstance(n, ast.Compare)]
    for field, expected in (("production", "BLOCKED"), ("real_broker_routing", "DISABLED")):
        assert any(isinstance(n.left, ast.Call)
                   and isinstance(n.left.func, ast.Attribute)
                   and n.left.func.attr == "get"
                   and n.left.args and isinstance(n.left.args[0], ast.Constant)
                   and n.left.args[0].value == field
                   and any(isinstance(op, ast.NotEq) for op in n.ops)
                   and any(isinstance(v, ast.Constant) and v.value == expected for v in n.comparators)
                   for n in comparisons)


def test_gateway_rejects_broker_receipt_with_changed_order_fields():
    tree = ast.parse(GATEWAY.read_text(encoding="utf-8"))
    submit = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "submit_order")
    comparisons = [n for n in ast.walk(submit) if isinstance(n, ast.Compare)]
    assert any(isinstance(n.left, ast.Call)
               and isinstance(n.left.func, ast.Attribute)
               and n.left.func.attr == "get"
               and any(isinstance(v, ast.Subscript) and isinstance(v.value, ast.Name)
                       and v.value.id == "paper_order" for v in n.comparators)
               and any(isinstance(op, ast.NotEq) for op in n.ops)
               for n in comparisons)
