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
