from __future__ import annotations


MODULES = [
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

def run_institutional_wiring(payload: dict | None = None) -> dict:
    # The historical factory includes arbitrary run()/health() hooks.
    # Until its call graph and symbol lineage are certified, neither may run.
    return {
        "program": "MIND_TRADER_INSTITUTIONAL_WIRING",
        "status": "NOT_CERTIFIED",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "modules_total": len(MODULES),
        "imports_ok": None,
        "runs_ok": None,
        "health_ok": None,
        "reason": "RUNTIME_CALL_GRAPH_NOT_CERTIFIED",
        "modules": list(MODULES),
    }


def _unsafe_legacy_institutional_wiring_disabled(payload: dict | None = None) -> dict:
    # Historical source remains recoverable in Git history. Never invoke.
    raise RuntimeError("UNVERIFIED_TRADER_WIRING_DISABLED")


def health() -> dict:
    # Health checks must not execute arbitrary imported trading modules.
    # No prior successful run evidence is available from this entrypoint.
    return {
        "status": "NOT_CERTIFIED",
        "modules_total": len(MODULES),
        "imports_ok": None,
        "runs_ok": None,
        "health_ok": None,
        "reason": "RUNTIME_EVIDENCE_NOT_VERIFIED",
    }

def run(payload: dict | None = None) -> dict:
    return run_institutional_wiring(payload)
