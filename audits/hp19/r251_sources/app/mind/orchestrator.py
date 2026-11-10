"""MIND Orchestrator v2 – high-level decision and tool routing.

This module provides a central orchestration layer that can:
- inspect user intent + context
- decide which subsystems to call (chat, search, creative, safety)
- build a lightweight "plan" that upstream code can execute

It is intentionally pure-Python and tolerant of missing subsystems.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


# Optional imports – all are best-effort only; orchestrator degrades gracefully.
try:  # pragma: no cover
    from app.search import universal_search  # type: ignore
except Exception:  # pragma: no cover
    universal_search = None  # type: ignore

try:  # pragma: no cover
    from app.creative import creative_os, creative_insights  # type: ignore
except Exception:  # pragma: no cover
    creative_os = None  # type: ignore
    creative_insights = None  # type: ignore

try:  # pragma: no cover
    from app.mind import graph_memory  # type: ignore
except Exception:  # pragma: no cover
    graph_memory = None  # type: ignore


class OrchestratorMode(str, Enum):
    """High-level strategy modes for the MIND agent."""

    CONVERSATION = "conversation"
    KNOWLEDGE_SEARCH = "knowledge_search"
    CREATIVE = "creative"
    DIAGNOSTIC = "diagnostic"


class ToolKind(str, Enum):
    """Logical tools the orchestrator can propose."""

    CHAT_LLM = "chat_llm"
    UNIVERSAL_SEARCH = "universal_search"
    GRAPH_CONTEXT = "graph_context"
    CREATIVE_OS = "creative_os"
    CREATIVE_INSIGHTS = "creative_insights"


@dataclass
class ToolCall:
    """Represents a single tool invocation in a plan."""

    kind: ToolKind
    params: Dict[str, Any]


@dataclass
class OrchestratorPlan:
    """High-level orchestration plan."""

    mode: OrchestratorMode
    tools: List[ToolCall]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "tools": [
                {"kind": tc.kind.value, "params": tc.params}
                for tc in self.tools
            ],
            "metadata": dict(self.metadata or {}),
        }


def _detect_mode(prompt: str) -> OrchestratorMode:
    """Very lightweight intent detection to choose a mode."""
    lowered = prompt.lower()

    if any(k in lowered for k in ["crie um vídeo", "criar vídeo", "sora", "roteiro", "campanha", "creative"]):
        return OrchestratorMode.CREATIVE

    if any(k in lowered for k in ["pesquise", "buscar", "search", "procurar", "encontre"]):
        return OrchestratorMode.KNOWLEDGE_SEARCH

    if any(k in lowered for k in ["debug", "erro", "log", "diagnóstico", "diagnostic"]):
        return OrchestratorMode.DIAGNOSTIC

    return OrchestratorMode.CONVERSATION


def build_plan(
    *,
    prompt: str,
    user_id: Optional[str],
    org_id: Optional[str],
    plan: Optional[str],
    extra_context: Optional[Dict[str, Any]] = None,
) -> OrchestratorPlan:
    """Build a high-level plan for how MIND should respond.

    This function does not call any external services directly; it only
    decides which subsystems should be involved and with which inputs.
    """
    mode = _detect_mode(prompt)
    tools: List[ToolCall] = []
    metadata: Dict[str, Any] = dict(extra_context or {})

    # Always include chat LLM as a base tool.
    tools.append(
        ToolCall(
            kind=ToolKind.CHAT_LLM,
            params={
                "prompt": prompt,
                "user_id": user_id,
                "org_id": org_id,
                "plan": plan,
            },
        )
    )

    if mode in {OrchestratorMode.KNOWLEDGE_SEARCH, OrchestratorMode.CONVERSATION}:
        if universal_search is not None:
            tools.append(
                ToolCall(
                    kind=ToolKind.UNIVERSAL_SEARCH,
                    params={
                        "query": prompt,
                        "limit_per_source": 4,
                    },
                )
            )

    if mode == OrchestratorMode.CREATIVE:
        if creative_os is not None:
            tools.append(
                ToolCall(
                    kind=ToolKind.CREATIVE_OS,
                    params={
                        "action": "ensure_project",
                        "user_id": user_id,
                        "org_id": org_id,
                    },
                )
            )
        if creative_insights is not None:
            tools.append(
                ToolCall(
                    kind=ToolKind.CREATIVE_INSIGHTS,
                    params={
                        "prompt": prompt,
                    },
                )
            )

    if graph_memory is not None:
        tools.append(
            ToolCall(
                kind=ToolKind.GRAPH_CONTEXT,
                params={
                    "center_ids": [user_id] if user_id else [],
                    "depth": 1,
                },
            )
        )

    metadata.update(
        {
            "user_id": user_id,
            "org_id": org_id,
            "plan": plan,
        }
    )
    return OrchestratorPlan(mode=mode, tools=tools, metadata=metadata)


def plan_as_dict(
    *,
    prompt: str,
    user_id: Optional[str],
    org_id: Optional[str],
    plan: Optional[str],
    extra_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """JSON-friendly wrapper around build_plan."""
    plan_obj = build_plan(
        prompt=prompt,
        user_id=user_id,
        org_id=org_id,
        plan=plan,
        extra_context=extra_context,
    )
    return plan_obj.to_dict()

