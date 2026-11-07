"""ET665.BG: no broker, no network, no execution; import only isolated policy modules."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_promotion_unknown_and_live_targets_fail_closed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mod = load("app/validation/promotion_authority.py", "et665_bg_promotion")
    for target in ("LIVE", "FTMO_REAL", "DEMO", "REPLAY", "PAPER ", "", None, [], {"mode": "PAPER"}):
        result = mod.promotion_authority("g", {"decision": "PAPER_TRADING_APPROVED"}, target)
        assert result["allowed"] is False
        assert result["decision"] == "FORCE_BLOCK_PROMOTION"


def test_promotion_only_paper_with_validation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mod = load("app/validation/promotion_authority.py", "et665_bg_promotion_ok")
    assert mod.promotion_authority("g", {"decision": "PAPER_TRADING_APPROVED"}, "PAPER")["allowed"] is True
    for invalid in ({}, None, "APPROVED"):
        assert mod.promotion_authority("g", invalid, "PAPER")["allowed"] is False


def test_p75_never_claims_transport_even_when_permission_true(monkeypatch):
    # Stub dependencies to avoid importing the wider application or any broker library.
    import sys
    import types
    pkg_names = [
        "app", "app.p74_mt5_demo_order_router_dry_run",
        "app.p69_73_mt5_ftmo_demo_governor",
    ]
    for name in pkg_names:
        pkg = types.ModuleType(name)
        pkg.__path__ = []
        monkeypatch.setitem(sys.modules, name, pkg)
    p74 = types.ModuleType("app.p74_mt5_demo_order_router_dry_run.engine")
    p74.build_demo_order = lambda: {"lot": 0.01}
    monkeypatch.setitem(sys.modules, p74.__name__, p74)
    gov = types.ModuleType("app.p69_73_mt5_ftmo_demo_governor.engine")
    gov.p71_pre_trade_governor = lambda *a, **kw: {"decision": "ALLOW_DEMO_TRADE"}
    monkeypatch.setitem(sys.modules, gov.__name__, gov)
    mod = load("app/p75_mt5_demo_order_execution_controlled/engine.py", "et665_bg_p75")
    assert mod.EXECUTION_ARMED is False
    blocked = mod.execute_demo_order_controlled(manual_confirmation=True)
    assert blocked["sent_to_mt5_demo"] is False
    monkeypatch.setattr(mod, "EXECUTION_ARMED", True)
    granted = mod.execute_demo_order_controlled(manual_confirmation=True)
    assert granted["permission_granted"] is True
    assert granted["sent_to_mt5_demo"] is False
    assert granted["execution_status"] == "DEMO_PERMISSION_ONLY_NOT_SENT"
    assert mod.execute_demo_order_controlled(account_mode="LIVE", manual_confirmation=True)["sent_to_mt5_demo"] is False
