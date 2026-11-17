import hashlib
import importlib.util
import sys
import types
from pathlib import Path

import pytest

from app.runtime.trader_paper_factory_guard import (
    PaperFactoryGateError,
    create_verified_paper_runtime,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app" / "runtime" / "mind_trader_institutional_wiring.py"
EXPECTED_SOURCE_SHA256 = "3e4a66308fdf69beec2a1de3309c68a14f8ad285787cd63eaf56a0fb237b7c42"

PAPER_ENV = {
    "TRADER_MODE": "PAPER_ONLY",
    "TRADER_LIVE": "FORBIDDEN",
    "TRADER_BROKER": "SIMULATED",
    "TRADER_NETWORK": "FORBIDDEN",
    "TRADER_ORDER_EXECUTION": "FORBIDDEN",
}
FTMO_CONFIG = {
    "version": "P8.46_FTMO_RULESET_V1",
    "account_size": 100000,
    "profit_target": 10000,
    "max_daily_loss": 5000,
    "max_total_loss": 10000,
    "minimum_trading_days": 4,
    "max_position_size": 1.0,
    "max_daily_trades": 5,
    "allowed_symbols": ["WIN", "WDO", "EURUSD", "XAUUSD"],
    "restricted_symbols": [],
    "allowed_sessions": ["09:00-17:00"],
    "restricted_news_events": True,
    "commission": 0.0,
    "spread": 0.0,
    "slippage": 0.0,
    "leverage": 100,
    "platform": "MT5",
    "challenge_type": "evaluation",
    "phase": "simulation",
}
FTMO_VALIDATION = {"valid": True, "reason": "FTMO_CONFIG_OK", "hash": "test-hash"}
HEALTH = {
    "status": "operational",
    "modules_total": 10,
    "imports_ok": 10,
    "runs_ok": 2,
    "health_ok": 0,
}
BROKER = {
    "broker": "PAPER_INTERNAL",
    "orders": 0,
    "accepted": 0,
    "rejected": 0,
    "production": "BLOCKED",
    "live": "FORBIDDEN",
    "edge_claim": "NONE",
}


def _install_package_chain(monkeypatch, dotted_name):
    parts = dotted_name.split(".")
    for index in range(1, len(parts)):
        name = ".".join(parts[:index])
        if name not in sys.modules:
            package = types.ModuleType(name)
            package.__path__ = []
            monkeypatch.setitem(sys.modules, name, package)


def _install_stub(monkeypatch, name, **attrs):
    _install_package_chain(monkeypatch, name)
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    monkeypatch.setitem(sys.modules, name, module)
    return module


def _load_original_factory(monkeypatch):
    _install_stub(
        monkeypatch,
        "mind_trader.app.risk.ftmo_ruleset",
        load_ftmo_config=lambda: (FTMO_CONFIG, FTMO_VALIDATION),
    )
    _install_stub(
        monkeypatch,
        "app.runtime.staging_v2.trader.mind_trader.app.execution.paper_broker_adapter",
        paper_broker_summary=lambda: BROKER,
    )
    spec = importlib.util.spec_from_file_location("trader_factory_under_test", SOURCE)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    module.health = lambda: HEALTH
    return module


def _set_paper_env(monkeypatch):
    for key, value in PAPER_ENV.items():
        monkeypatch.setenv(key, value)


def test_original_factory_bytes_match_drive_authority():
    assert SOURCE.stat().st_size == 6371
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED_SOURCE_SHA256


def test_recovered_factory_composes_inert_paper_runtime(monkeypatch):
    _set_paper_env(monkeypatch)
    factory = _load_original_factory(monkeypatch)

    composition = create_verified_paper_runtime(factory)

    assert composition.mode == "PAPER_ONLY"
    assert composition.broker_mode == "SIMULATED"
    assert composition.live_real == "FORBIDDEN"
    assert composition.network_access == "FORBIDDEN"
    assert composition.order_execution == "FORBIDDEN"
    assert composition.health_snapshot == HEALTH
    assert composition.ftmo_config == (FTMO_CONFIG, FTMO_VALIDATION)
    assert composition.paper_broker_snapshot == BROKER


@pytest.mark.parametrize(
    "key,bad_value",
    [
        ("TRADER_MODE", "LIVE"),
        ("TRADER_LIVE", "ALLOWED"),
        ("TRADER_BROKER", "REAL"),
        ("TRADER_NETWORK", "ALLOWED"),
        ("TRADER_ORDER_EXECUTION", "ALLOWED"),
    ],
)
def test_environment_violation_fails_before_loading_config(monkeypatch, key, bad_value):
    _set_paper_env(monkeypatch)
    monkeypatch.setenv(key, bad_value)
    factory = _load_original_factory(monkeypatch)
    calls = {"loader": 0, "factory": 0}
    factory._trader_canonical_load_ftmo_config = lambda: calls.__setitem__("loader", calls["loader"] + 1)
    factory.create_paper_runtime = lambda: calls.__setitem__("factory", calls["factory"] + 1)

    with pytest.raises(PaperFactoryGateError, match="PAPER_ONLY environment"):
        create_verified_paper_runtime(factory)

    assert calls == {"loader": 0, "factory": 0}


@pytest.mark.parametrize(
    "config,validation",
    [
        (None, {"valid": False, "reason": "CONFIG_FILE_NOT_FOUND"}),
        (FTMO_CONFIG, {"valid": False, "reason": "INVALID"}),
        ({**FTMO_CONFIG, "phase": "live"}, FTMO_VALIDATION),
        ({**FTMO_CONFIG, "spread": -1}, FTMO_VALIDATION),
        ({**FTMO_CONFIG, "commission": float("inf")}, FTMO_VALIDATION),
    ],
)
def test_invalid_ftmo_config_fails_before_factory_execution(monkeypatch, config, validation):
    _set_paper_env(monkeypatch)
    factory = _load_original_factory(monkeypatch)
    calls = {"factory": 0}
    factory._trader_canonical_load_ftmo_config = lambda: (config, validation)
    factory.create_paper_runtime = lambda: calls.__setitem__("factory", calls["factory"] + 1)

    with pytest.raises(PaperFactoryGateError, match="FTMO configuration"):
        create_verified_paper_runtime(factory)

    assert calls["factory"] == 0


def test_incomplete_health_snapshot_is_rejected(monkeypatch):
    _set_paper_env(monkeypatch)
    factory = _load_original_factory(monkeypatch)
    factory.health = lambda: {**HEALTH, "imports_ok": 9}

    with pytest.raises(PaperFactoryGateError, match="health is incomplete"):
        create_verified_paper_runtime(factory)


def test_broker_live_flag_is_rejected(monkeypatch):
    _set_paper_env(monkeypatch)
    factory = _load_original_factory(monkeypatch)
    factory._trader_canonical_paper_broker_summary = lambda: {**BROKER, "live": "ALLOWED"}

    with pytest.raises(PaperFactoryGateError, match="broker snapshot"):
        create_verified_paper_runtime(factory)


def test_ftmo_config_drift_between_preflight_and_composition_is_rejected(monkeypatch):
    _set_paper_env(monkeypatch)
    factory = _load_original_factory(monkeypatch)
    calls = {"count": 0}

    def changing_loader():
        calls["count"] += 1
        if calls["count"] == 1:
            return FTMO_CONFIG, FTMO_VALIDATION
        changed = {**FTMO_CONFIG, "spread": 0.5}
        return changed, FTMO_VALIDATION

    factory._trader_canonical_load_ftmo_config = changing_loader

    with pytest.raises(PaperFactoryGateError, match="changed during"):
        create_verified_paper_runtime(factory)


def test_module_inventory_is_exact_and_matches_guard_contract(monkeypatch):
    factory = _load_original_factory(monkeypatch)
    assert factory.MODULES == [
        "app.runtime.p2223_broker_emulator",
        "app.runtime.p2224_2226_institutional_core",
        "app.runtime.p2227_2229_advanced_layer",
        "app.runtime.p2131_2150_ftmo_paper_compliance_assurance",
        "app.runtime.p2081_2090_realtime_portfolio_governance",
        "app.runtime.p2091_2100_realtime_intelligence_layer",
        "app.runtime.p2071_2080_realtime_paper_runtime",
        "app.runtime.p19_governance_layer",
        "app.runtime.capability_usage_ledger",
        "app.modules.usde_core.scientific_ledger",
    ]
    from app.runtime import trader_paper_factory_guard as guard
    assert len(factory.MODULES) == guard.EXPECTED_MODULES == 10
    assert guard.EXPECTED_MODULE_RUNS == 2


def test_original_wiring_aggregates_only_the_ten_allowlisted_modules(monkeypatch):
    factory = _load_original_factory(monkeypatch)
    fake_modules = {}
    for index, module_name in enumerate(factory.MODULES):
        fake = types.ModuleType(module_name)
        if index in (1, 2):
            fake.run = lambda payload=None: {"status": "PASS", "mode": "simulation"}
        fake_modules[module_name] = fake
    monkeypatch.setattr(factory.importlib, "import_module", lambda name: fake_modules[name])

    result = factory.run_institutional_wiring({"mode": "PAPER_ONLY"})

    assert result["modules_total"] == 10
    assert result["imports_ok"] == 10
    assert result["runs_ok"] == 2
    assert result["mode"] == "PAPER_ONLY"
    assert result["real_orders"] == "FORBIDDEN"
    assert result["ftmo_real"] == "FORBIDDEN"
    assert [row["module"] for row in result["results"]] == list(factory.MODULES)
