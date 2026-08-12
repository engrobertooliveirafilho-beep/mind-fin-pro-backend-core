from __future__ import annotations

import os
from typing import Any, Dict


def assisted_bypass_enabled() -> bool:
    return os.getenv("MIND_ENABLE_MINDOS_ASSISTED_BYPASS", "0") == "1"


def build_universal_assisted_context(inbound_text: str) -> Dict[str, Any]:
    """
    Universal adapter only.
    No hardcoded domain answers.
    No direct capability execution.
    No production action.
    """
    text = str(inbound_text or "").strip()

    result: Dict[str, Any] = {
        "mode": "UNIVERSAL_ASSISTED_ADAPTER",
        "enabled": assisted_bypass_enabled(),
        "inbound_preview": text[:300],
        "send_to_user": False,
        "execution_allowed": False,
        "production_allowed": False,
        "shadow_only": True,
        "ok": False,
        "error": None,
        "capability_chain": None,
        "knowledge_context": None,
        "execution_graph": None,
        "candidate_text": "",
    }

    if not result["enabled"]:
        return result

    try:
        from app.runtime.capability_governance.capability_composer import compose_capabilities
        from app.runtime.knowledge_fusion.knowledge_fusion_engine import fuse_knowledge
        from app.runtime.execution_graph.execution_graph_dag import build_execution_dag

        result["capability_chain"] = compose_capabilities(text)
        result["knowledge_context"] = fuse_knowledge(text)
        result["execution_graph"] = build_execution_dag(text)

        graph = result.get("execution_graph") or {}
        chain = result.get("capability_chain") or {}

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
        chain_len = chain.get("chain_length")
        node_count = graph.get("node_count")

        result["candidate_text"] = (
            f"[MIND-OS_ASSISTED_CANDIDATE] "
            f"intent={intent}; chain_length={chain_len}; node_count={node_count}; "
            f"final_authority_required={graph.get('final_authority_required')}; "
            f"execution_allowed={graph.get('execution_allowed')}; "
            f"production_allowed={graph.get('production_allowed')}"
        )

        result["ok"] = True

        try:
            from app.runtime.universal_authority_renderer import render_universal_authority_candidate
            result["authority_render"] = render_universal_authority_candidate(result)
        except Exception as render_exc:
            result["authority_render"] = {
                "ok": False,
                "send_to_user": False,
                "error": f"{type(render_exc).__name__}: {render_exc}",
            }

        return result

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result


def build_assisted_bypass_reply(inbound_text: str) -> str:
    """
    Compatibility function for whatsapp.py hook.
    Deliberately returns empty string.
    This prevents hardcoded replies from bypassing the universal authority layer.
    """
    ctx = build_universal_assisted_context(inbound_text)

    if not ctx.get("enabled"):
        return ""

    # No direct response until a real universal authority renderer exists.
    return ""


