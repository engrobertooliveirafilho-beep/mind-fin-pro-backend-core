"""Agent Profiles and registry for MIND FIN PRO.

This module defines configurable "agent profiles" that control how the
MIND orchestrator and downstream tools should behave for different
contexts (free, pro, enterprise, internal, etc.).

Each profile defines:
- system persona / description
- safety level and behavior
- allowed tools and capabilities
- hints for quotas, plans and creative behavior

The implementation is in-memory, designed to be backed by DB/config
later without breaking the public API.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional


@dataclass
class SafetyPolicy:
    """Safety behavior for an agent profile."""

    level: str  # e.g. "strict", "standard", "relaxed"
    allow_review_flow: bool = True
    allow_soft_override: bool = False


@dataclass
class ToolPolicy:
    """Tool usage policy for an agent profile."""

    allowed_tools: List[str] = field(default_factory=list)
    default_mode: str = "conversation"  # conversation|creative|mixed
    enable_universal_search: bool = True
    enable_creative_stack: bool = True
    enable_experiments: bool = True


@dataclass
class AgentProfile:
    """Single agent profile for MIND."""

    id: str
    name: str
    description: str
    safety: SafetyPolicy
    tools: ToolPolicy
    plan_hint: Optional[str] = None
    org_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["safety"] = asdict(self.safety)
        data["tools"] = asdict(self.tools)
        return data


_PROFILES: Dict[str, AgentProfile] = {}


def register_profile(profile: AgentProfile) -> None:
    """Register or replace an agent profile."""
    _PROFILES[profile.id] = profile


def get_profile(profile_id: str) -> Optional[AgentProfile]:
    """Return an agent profile by id, or None if not found."""
    return _PROFILES.get(profile_id)


def list_profiles() -> List[Dict[str, Any]]:
    """Return all profiles as JSON-friendly dicts."""
    return [p.to_dict() for p in _PROFILES.values()]


def resolve_profile_for_context(
    *,
    explicit_profile_id: Optional[str],
    plan: Optional[str],
    org_id: Optional[str],
) -> AgentProfile:
    """Resolve the best profile for the given context.

    Resolution order:
    1) explicit_profile_id if provided and found
    2) plan-based default (enterprise/pro/free)
    3) global fallback "mind-default"
    """
    if explicit_profile_id:
        p = get_profile(explicit_profile_id)
        if p is not None:
            return p

    normalized_plan = (plan or "free").lower()
    if "enterprise" in normalized_plan:
        p = get_profile("mind-enterprise")
        if p is not None:
            return p
    elif "pro" in normalized_plan:
        p = get_profile("mind-pro")
        if p is not None:
            return p
    else:
        p = get_profile("mind-free")
        if p is not None:
            return p

    # Guaranteed to exist after _bootstrap_defaults.
    return _PROFILES["mind-default"]


def _bootstrap_defaults() -> None:
    """Initialize a small set of built-in profiles."""
    # Global default profile (safe, mixed usage).
    register_profile(
        AgentProfile(
            id="mind-default",
            name="MIND Default",
            description="Perfil padrão da MIND, focado em conversa segura e criatividade básica.",
            safety=SafetyPolicy(level="standard", allow_review_flow=True, allow_soft_override=False),
            tools=ToolPolicy(
                allowed_tools=[
                    "chat_llm",
                    "universal_search",
                    "creative_os",
                    "creative_insights",
                    "graph_context",
                ],
                default_mode="conversation",
                enable_universal_search=True,
                enable_creative_stack=True,
                enable_experiments=False,
            ),
            plan_hint=None,
            org_hint=None,
        )
    )

    # Free plan – more conservative and com menos ferramentas.
    register_profile(
        AgentProfile(
            id="mind-free",
            name="MIND Free",
            description="Perfil para plano Free, foco em segurança máxima e recursos limitados.",
            safety=SafetyPolicy(level="strict", allow_review_flow=True, allow_soft_override=False),
            tools=ToolPolicy(
                allowed_tools=[
                    "chat_llm",
                    "universal_search",
                ],
                default_mode="conversation",
                enable_universal_search=True,
                enable_creative_stack=False,
                enable_experiments=False,
            ),
            plan_hint="free",
            org_hint=None,
        )
    )

    # Pro – criativo com stack completa, mas ainda seguro.
    register_profile(
        AgentProfile(
            id="mind-pro",
            name="MIND Pro",
            description="Perfil Pro com foco em criatividade e campanhas, mantendo safety forte.",
            safety=SafetyPolicy(level="standard", allow_review_flow=True, allow_soft_override=True),
            tools=ToolPolicy(
                allowed_tools=[
                    "chat_llm",
                    "universal_search",
                    "creative_os",
                    "creative_insights",
                    "graph_context",
                    "experiments",
                ],
                default_mode="creative",
                enable_universal_search=True,
                enable_creative_stack=True,
                enable_experiments=True,
            ),
            plan_hint="pro",
            org_hint=None,
        )
    )

    # Enterprise – máximo de flexibilidade, para squads avançadas.
    register_profile(
        AgentProfile(
            id="mind-enterprise",
            name="MIND Enterprise",
            description="Perfil Enterprise com orquestração avançada, experiments e maior autonomia.",
            safety=SafetyPolicy(level="standard", allow_review_flow=True, allow_soft_override=True),
            tools=ToolPolicy(
                allowed_tools=[
                    "chat_llm",
                    "universal_search",
                    "creative_os",
                    "creative_insights",
                    "graph_context",
                    "experiments",
                ],
                default_mode="mixed",
                enable_universal_search=True,
                enable_creative_stack=True,
                enable_experiments=True,
            ),
            plan_hint="enterprise",
            org_hint=None,
        )
    )


# Ensure default profiles are present on import.
_bootstrap_defaults()

