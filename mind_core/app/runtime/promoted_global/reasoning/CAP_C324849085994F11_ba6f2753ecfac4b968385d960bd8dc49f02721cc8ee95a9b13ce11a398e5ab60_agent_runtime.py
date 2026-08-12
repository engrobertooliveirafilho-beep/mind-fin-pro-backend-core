from __future__ import annotations
import os
"""Agent Runtime – executes MIND plans end-to-end.

This module takes a prompt and context, uses the agent router/orchestrator
to build a plan, and then executes tools in-process where possible.

It is designed as a thin runtime layer:
- no hard external dependencies
- tolerant of missing subsystems
- JSON-friendly output for API/worker layers
"""


from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


# Optional imports (all guarded; runtime must degrade gracefully).
try:  # pragma: no cover
    from app.mind import agent_router
except Exception:  # pragma: no cover
    agent_router = None  # type: ignore

try:  # pragma: no cover
    from app.search import universal_search as universal_search_module
except Exception:  # pragma: no cover
    universal_search_module = None  # type: ignore

try:  # pragma: no cover
    from app.mind import graph_memory
except Exception:  # pragma: no cover
    graph_memory = None  # type: ignore

try:  # pragma: no cover
    from app.creative import creative_os, creative_insights
except Exception:  # pragma: no cover
    creative_os = None  # type: ignore
    creative_insights = None  # type: ignore


@dataclass
class ToolExecutionResult:
    """Single tool execution result."""

    kind: str
    ok: bool
    payload: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class AgentTurnResult:
    """Full result for a single agent turn."""

    profile: Dict[str, Any]
    plan: Dict[str, Any]
    tools: List[ToolExecutionResult]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": self.profile,
            "plan": self.plan,
            "tools": [
                {
                    "kind": t.kind,
                    "ok": t.ok,
                    "payload": t.payload,
                    "error": t.error,
                }
                for t in self.tools
            ],
        }


def _exec_universal_search(params: Dict[str, Any]) -> ToolExecutionResult:
    if universal_search_module is None:  # pragma: no cover
        return ToolExecutionResult(
            kind="universal_search",
            ok=False,
            payload={},
            error="universal_search module not available",
        )
    try:  # pragma: no cover
        query = str(params.get("query", ""))
        limit_per_source = int(params.get("limit_per_source", 4))
        result = universal_search_module.universal_search_as_dict(  # type: ignore[attr-defined]
            query=query,
            limit_per_source=limit_per_source,
        )
        return ToolExecutionResult(kind="universal_search", ok=True, payload=result)
    except Exception as exc:  # pragma: no cover
        return ToolExecutionResult(
            kind="universal_search",
            ok=False,
            payload={},
            error=str(exc),
        )


def _exec_graph_context(params: Dict[str, Any]) -> ToolExecutionResult:
    if graph_memory is None:
        return ToolExecutionResult(
            kind="graph_context",
            ok=False,
            payload={},
            error="graph_memory module not available",
        )
    try:
        center_ids = params.get("center_ids") or []
        depth = int(params.get("depth", 1))
        snap = graph_memory.get_context_subgraph(  # type: ignore[attr-defined]
            center_ids=center_ids,
            depth=depth,
        )
        payload = {"nodes": snap.nodes, "edges": snap.edges}
        return ToolExecutionResult(kind="graph_context", ok=True, payload=payload)
    except Exception as exc:
        return ToolExecutionResult(
            kind="graph_context",
            ok=False,
            payload={},
            error=str(exc),
        )


def _exec_creative_os(params: Dict[str, Any]) -> ToolExecutionResult:
    if creative_os is None:
        return ToolExecutionResult(
            kind="creative_os",
            ok=False,
            payload={},
            error="creative_os module not available",
        )
    try:  # pragma: no cover - depends on creative_os implementation
        action = params.get("action") or "ensure_project"
        if action == "ensure_project":
            # Minimal generic call; concrete wiring is left for future STEPs.
            result = {"status": "noop", "reason": "ensure_project not wired yet"}
        else:
            result = {"status": "noop", "reason": f"unknown action: {action}"}
        return ToolExecutionResult(kind="creative_os", ok=True, payload=result)
    except Exception as exc:
        return ToolExecutionResult(
            kind="creative_os",
            ok=False,
            payload={},
            error=str(exc),
        )


def _exec_creative_insights(params: Dict[str, Any]) -> ToolExecutionResult:
    if creative_insights is None:
        return ToolExecutionResult(
            kind="creative_insights",
            ok=False,
            payload={},
            error="creative_insights module not available",
        )
    try:  # pragma: no cover - depends on creative_insights implementation
        prompt = str(params.get("prompt", ""))
        if hasattr(creative_insights, "analyze_prompt"):  # type: ignore[attr-defined]
            insights = creative_insights.analyze_prompt(prompt=prompt)  # type: ignore[attr-defined]
        else:
            insights = {"status": "noop", "reason": "analyze_prompt not implemented"}
        return ToolExecutionResult(kind="creative_insights", ok=True, payload=insights)
    except Exception as exc:
        return ToolExecutionResult(
            kind="creative_insights",
            ok=False,
            payload={},
            error=str(exc),
        )


def _exec_chat_llm(params: Dict[str, Any]) -> ToolExecutionResult:
    """Placeholder for chat LLM execution.

    Real implementation will call the configured LLM provider; here we
    only echo back a structured stub so the runtime can be observed.
    """
    prompt = str(params.get("prompt", ""))
    metadata = {k: v for k, v in params.items() if k != "prompt"}
    payload = {
        "status": "stub",
        "echo": prompt,
        "metadata": metadata,
    }
    return ToolExecutionResult(kind="chat_llm", ok=True, payload=payload)


def _execute_tool(kind: str, params: Dict[str, Any]) -> ToolExecutionResult:
    if kind == "universal_search":
        return _exec_universal_search(params)
    if kind == "graph_context":
        return _exec_graph_context(params)
    if kind == "creative_os":
        return _exec_creative_os(params)
    if kind == "creative_insights":
        return _exec_creative_insights(params)
    if kind == "chat_llm":
        return _exec_chat_llm(params)

    return ToolExecutionResult(
        kind=kind,
        ok=False,
        payload={},
        error="unknown tool kind",
    )


def run_agent_turn(
    *,
    prompt: str,
    user_id: Optional[str],
    org_id: Optional[str],
    plan: Optional[str],
    explicit_profile_id: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> AgentTurnResult:
    """Execute a full agent turn:

    1) Resolve profile + plan via agent_router (if available)
    2) Execute each tool in the plan with safe fallbacks
    """
    if agent_router is None:
        # Minimal fallback: chat-only stub.
        plan = {
            "mode": "conversation",
            "tools": [
                {"kind": "chat_llm", "params": {"prompt": prompt}},
            ],
            "metadata": {},
        }
        profile = {
            "id": "fallback",
            "name": "Fallback profile",
            "description": "Agent router unavailable; using chat-only fallback.",
        }
    else:
        routing = agent_router.routing_result_as_dict(  # type: ignore[attr-defined]
            prompt=prompt,
            user_id=user_id,
            org_id=org_id,
            plan=plan,
            explicit_profile_id=explicit_profile_id,
            extra_context=extra_context or {},
        )
        profile = routing.get("profile", {})
        plan = routing.get("plan", {})

    tools_specs = plan.get("tools") or []
    tool_results: List[ToolExecutionResult] = []
    for spec in tools_specs:
        kind = str(spec.get("kind", ""))
        params = spec.get("params") or {}
        res = _execute_tool(kind=kind, params=params)
        tool_results.append(res)

    return AgentTurnResult(
        profile=profile,
        plan=plan,
        tools=tool_results,
    )


def run_agent_turn_as_dict(
    *,
    prompt: str,
    user_id: Optional[str],
    org_id: Optional[str],
    plan: Optional[str],
    explicit_profile_id: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """JSON-friendly wrapper for run_agent_turn."""
    result = run_agent_turn(
        prompt=prompt,
        user_id=user_id,
        org_id=org_id,
        plan=plan,
        explicit_profile_id=explicit_profile_id,
        extra_context=extra_context,
    )
    return result.to_dict()
