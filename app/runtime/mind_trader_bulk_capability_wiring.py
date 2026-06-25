from __future__ import annotations
import importlib
from datetime import datetime, timezone

BULK_MODULES = [
  "app.modules.usde_core.scientific_knowledge_sync",
  "app.modules.usde_core.scientific_knowledge_graph",
  "app.runtime.response_builder",
  "app.runtime.cognitive_pipeline",
  "app.modules.usde_core.meta_learning_engine",
  "app.modules.usde_core.tda_engine",
  "app.runtime.response_strategy",
  "app.runtime.drive_capability_absorption",
  "app.runtime.real_humanization_runtime",
  "app.runtime.p19_governance_layer",
  "app.modules.usde_core.scientific_os",
  "app.runtime.system_memory_contract",
  "app.runtime.knowledge_extraction_engine",
  "app.runtime.canary_gate",
  "app.runtime.drive_processed_queue",
  "app.modules.usde_core.scientific_pipeline",
  "app.runtime.capability_usage_ledger",
  "app.modules.usde_core.scientific_ledger",
  "app.modules.usde_core.ledger",
  "app.modules.usde_core.experiment_runner",
  "app.runtime.context_priority_engine",
  "app.runtime.p2224_2226_institutional_core",
  "app.runtime.p2227_2229_advanced_layer",
  "app.modules.usde_core.scientific_governance_engine",
  "app.runtime.p2223_broker_emulator",
  "app.runtime.generic_conversation_state",
  "app.runtime.social_observation_runtime",
  "app.p10_activation_stack.risk_governance",
  "app.runtime.capability_reconstruction_planner",
  "app.modules.usde_core.theorem_engine",
  "app.runtime.advanced_runtime_base",
  "app.runtime.final_conversational_arbiter",
  "app.runtime.hallucination_guard",
  "app.runtime.persistent_dialogue_state",
  "app.runtime.social_cognition_engine",
  "app.runtime.trusted_sources_engine",
  "app.runtime.provider_health_runtime",
  "app.runtime.persistent_social_memory",
  "app.runtime.anti_repetition_engine",
  "app.modules.usde_core.red_team_engine",
  "app.runtime.human_reflection_engine",
  "app.runtime.persistent_emotional_state",
  "app.runtime.universal_conversation_os",
  "app.runtime.contextual_followup_engine",
  "app.runtime.natural_transition_engine",
  "app.runtime.conversation_continuity_engine",
  "app.modules.usde_core.evidence_engine",
  "app.runtime.semantic_dialogue_memory",
  "app.runtime.emotional_continuity_engine",
  "app.runtime.robotic_detector",
  "app.runtime.response_naturalness_score",
  "app.runtime.realtime_tool_router",
  "app.runtime.provider_runtime_matrix",
  "app.runtime.provider_fallback_runtime",
  "app.runtime.provider_cost_router",
  "app.runtime.safe_external_search"
]

def run_bulk_capability_wiring(payload: dict | None = None) -> dict:
    payload = payload or {}
    results = []
    for name in BULK_MODULES:
        row = {"module": name, "import_ok": False, "run_ok": False, "health_ok": False, "error": ""}
        try:
            m = importlib.import_module(name)
            row["import_ok"] = True
            if hasattr(m, "health"):
                try:
                    row["health_ok"] = isinstance(m.health(), dict)
                except Exception as e:
                    row["error"] += f"health_error={e};"
            if hasattr(m, "run"):
                try:
                    try:
                        out = m.run(payload)
                    except TypeError:
                        out = m.run()
                    row["run_ok"] = out is not None
                except Exception as e:
                    row["error"] += f"run_error={e};"
        except Exception as e:
            row["error"] = str(e)
        results.append(row)

    return {
        "program": "MIND_TRADER_BULK_CAPABILITY_WIRING",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "modules_total": len(results),
        "imports_ok": sum(1 for r in results if r["import_ok"]),
        "runs_ok": sum(1 for r in results if r["run_ok"]),
        "health_ok": sum(1 for r in results if r["health_ok"]),
        "results": results,
    }

def run(payload: dict | None = None) -> dict:
    return run_bulk_capability_wiring(payload)

def health() -> dict:
    out = run_bulk_capability_wiring({})
    return {
        "status": "OK" if out["imports_ok"] == out["modules_total"] else "DEGRADED",
        "modules_total": out["modules_total"],
        "imports_ok": out["imports_ok"],
        "runs_ok": out["runs_ok"],
        "health_ok": out["health_ok"],
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }
