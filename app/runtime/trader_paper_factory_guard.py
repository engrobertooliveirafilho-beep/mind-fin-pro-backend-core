from __future__ import annotations

import importlib
import math
from numbers import Real
from typing import Any


class PaperFactoryGateError(RuntimeError):
    """Raised when the recovered Trader factory cannot prove a safe PAPER composition."""


EXPECTED_MODULES = 10
EXPECTED_MODULE_RUNS = 2
_REQUIRED_BROKER_FLAGS = {
    "broker": "PAPER_INTERNAL",
    "production": "BLOCKED",
    "live": "FORBIDDEN",
    "edge_claim": "NONE",
}


def _valid_ftmo_snapshot(value: Any) -> bool:
    if not isinstance(value, tuple) or len(value) != 2:
        return False
    config, validation = value
    if not isinstance(config, dict) or not isinstance(validation, dict):
        return False
    if validation.get("valid") is not True:
        return False
    if config.get("phase") != "simulation":
        return False
    for field in ("commission", "spread", "slippage"):
        amount = config.get(field)
        if isinstance(amount, bool) or not isinstance(amount, Real):
            return False
        if not math.isfinite(float(amount)) or amount < 0:
            return False
    return True


def create_verified_paper_runtime(factory_module: Any | None = None) -> Any:
    """
    Gate the byte-recovered institutional factory before a PAPER composition
    can be handed to a writer or dispatcher. This function never sends orders.
    """
    factory = factory_module or importlib.import_module(
        "app.runtime.mind_trader_institutional_wiring"
    )

    require_environment = getattr(factory, "_require_paper_only_environment", None)
    load_ftmo_config = getattr(factory, "_trader_canonical_load_ftmo_config", None)
    create_runtime = getattr(factory, "create_paper_runtime", None)

    if not callable(require_environment) or not callable(load_ftmo_config) or not callable(create_runtime):
        raise PaperFactoryGateError("recovered factory contract is incomplete")

    try:
        require_environment()
    except Exception as exc:
        raise PaperFactoryGateError("PAPER_ONLY environment rejected") from exc

    try:
        ftmo_preflight = load_ftmo_config()
    except Exception as exc:
        raise PaperFactoryGateError("FTMO configuration could not be loaded") from exc

    if not _valid_ftmo_snapshot(ftmo_preflight):
        raise PaperFactoryGateError("FTMO configuration is missing, invalid, or not simulation-only")

    try:
        composition = create_runtime()
    except Exception as exc:
        raise PaperFactoryGateError("canonical PAPER factory failed") from exc

    if composition.ftmo_config != ftmo_preflight:
        raise PaperFactoryGateError("FTMO configuration changed during factory composition")

    if (
        composition.mode != "PAPER_ONLY"
        or composition.broker_mode != "SIMULATED"
        or composition.live_real != "FORBIDDEN"
        or composition.network_access != "FORBIDDEN"
        or composition.order_execution != "FORBIDDEN"
    ):
        raise PaperFactoryGateError("PAPER composition safety flags do not match the contract")

    health = composition.health_snapshot
    if not isinstance(health, dict):
        raise PaperFactoryGateError("factory health snapshot is not a dictionary")
    if (
        health.get("status") != "operational"
        or health.get("modules_total") != EXPECTED_MODULES
        or health.get("imports_ok") != EXPECTED_MODULES
        or health.get("runs_ok") != EXPECTED_MODULE_RUNS
    ):
        raise PaperFactoryGateError("institutional module health is incomplete")

    broker = composition.paper_broker_snapshot
    if not isinstance(broker, dict) or any(
        broker.get(key) != expected
        for key, expected in _REQUIRED_BROKER_FLAGS.items()
    ):
        raise PaperFactoryGateError("paper broker snapshot does not prove an inert PAPER broker")

    return composition
