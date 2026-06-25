from datetime import datetime, timezone

def run_level_a_shadow(message: str = "", sender_id: str = "unknown", context: dict | None = None):
    context = context or {}

    trace = {
        "status": "ok",
        "mode": "shadow_only",
        "sender_id": sender_id,
        "message": message,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "capabilities": {
            "semantic_memory": False,
            "context_recovery": False,
            "contextual_continuity": False,
            "hierarchical_planner": False,
            "autonomous_planner": False,
        },
        "signals": [],
        "recommendation": None,
    }

    lower = (message or "").lower()

    if any(x in lower for x in ["aks", "mercedes", "classe a", "marcha", "embreagem", "atuador"]):
        trace["capabilities"]["context_recovery"] = True
        trace["capabilities"]["contextual_continuity"] = True
        trace["capabilities"]["hierarchical_planner"] = True
        trace["capabilities"]["autonomous_planner"] = True
        trace["signals"].append("technical_vehicle_diagnostic_context")
        trace["recommendation"] = (
            "Detectado contexto técnico automotivo. "
            "Resposta final deveria usar diagnóstico incremental, histórico e hipótese por eliminação."
        )

    if context:
        trace["capabilities"]["semantic_memory"] = True
        trace["signals"].append("context_available")

    return trace
