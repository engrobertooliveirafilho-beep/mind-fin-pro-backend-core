from __future__ import annotations

from typing import Any, Dict, List


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def render_universal_authority_candidate(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Universal renderer.
    No hardcoded domain replies.
    No direct execution.
    No production action.
    Produces an audit-safe candidate from MIND-OS context.
    """
    result: Dict[str, Any] = {
        "mode": "UNIVERSAL_AUTHORITY_RENDERER",
        "ok": False,
        "send_to_user": False,
        "execution_allowed": False,
        "production_allowed": False,
        "shadow_only": True,
        "error": None,
        "text": "",
        "quality": {
            "has_intent": False,
            "has_chain": False,
            "has_graph": False,
            "has_knowledge": False,
            "safe": False,
        },
    }

    if not isinstance(ctx, dict):
        result["error"] = "context_not_dict"
        return result

    if ctx.get("ok") is not True:
        result["error"] = "context_not_ok"
        return result

    graph = ctx.get("execution_graph") or {}
    chain = ctx.get("capability_chain") or {}
    knowledge = ctx.get("knowledge_context") or {}

    if not isinstance(graph, dict) or not isinstance(chain, dict) or not isinstance(knowledge, dict):
        result["error"] = "invalid_context_shapes"
        return result

    if graph.get("execution_allowed") is not False:
        result["error"] = "unsafe_execution_allowed"
        return result

    if graph.get("production_allowed") is not False:
        result["error"] = "unsafe_production_allowed"
        return result

    if graph.get("shadow_only") is not True:
        result["error"] = "not_shadow_only"
        return result

    intent = graph.get("intent") or chain.get("intent") or "assist"
    chain_items = _safe_list(chain.get("capability_chain"))
    fused_items = _safe_list(knowledge.get("fused_capability_chain"))

    roles = []
    for item in chain_items:
        if isinstance(item, dict) and item.get("role"):
            roles.append(str(item.get("role")))

    evidence_roles = []
    for item in fused_items:
        if isinstance(item, dict) and item.get("role"):
            evidence_roles.append(str(item.get("role")))

    node_count = graph.get("node_count")
    edge_count = graph.get("edge_count")
    is_dag = graph.get("is_dag")

    result["quality"] = {
        "has_intent": bool(intent),
        "has_chain": len(roles) > 0,
        "has_graph": is_dag is True and node_count is not None,
        "has_knowledge": len(evidence_roles) > 0,
        "safe": True,
    }

    lines = []
    lines.append(f"Intenção detectada: {intent}.")
    lines.append(f"Plano interno: {len(roles)} capacidades, {node_count} nós e {edge_count} conexões.")
    if roles:
        lines.append("Capacidades envolvidas: " + "; ".join(roles[:5]) + ".")
    if evidence_roles:
        lines.append("Evidência técnica disponível para: " + "; ".join(evidence_roles[:5]) + ".")
    lines.append("Execução direta continua bloqueada; resposta final exige autoridade.")

    result["text"] = " ".join(lines).strip()
    result["ok"] = True
    return result
