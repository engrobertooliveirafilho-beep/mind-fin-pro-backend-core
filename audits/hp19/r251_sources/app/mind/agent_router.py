"""Agent Router – bridge between profiles and orchestrator.

This module connects:
- Agent profiles (safety + tools + plan hints)
- Orchestrator (tool planning and routing)

It provides a single entry point that:
- resolves the best profile for a given context
- builds an orchestrator plan seeded with that profile
- returns a JSON-friendly payload for higher layers (API, workers, etc.)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

from app.mind import agent_profiles, orchestrator


@dataclass
class AgentRoutingResult:
    """Result of routing a request through profile + orchestrator."""

    profile: Dict[str, Any]
    plan: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": dict(self.profile),
            "plan": dict(self.plan),
        }


def build_routing_result(
    *,
    prompt: str,
    user_id: Optional[str],
    org_id: Optional[str],
    plan: Optional[str],
    explicit_profile_id: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> AgentRoutingResult:
    """Resolve profile and build orchestrator plan for a request."""
    profile_obj = agent_profiles.resolve_profile_for_context(
        explicit_profile_id=explicit_profile_id,
        plan=plan,
        org_id=org_id,
    )
    profile_dict = profile_obj.to_dict()

    context = dict(extra_context or {})
    context.update(
        {
            "profile_id": profile_obj.id,
            "profile_name": profile_obj.name,
            "profile_safety_level": profile_obj.safety.level,
            "profile_default_mode": profile_obj.tools.default_mode,
        }
    )

    plan_dict = orchestrator.plan_as_dict(
        prompt=prompt,
        user_id=user_id,
        org_id=org_id,
        plan=plan,
        extra_context=context,
    )

    return AgentRoutingResult(profile=profile_dict, plan=plan_dict)


def routing_result_as_dict(
    *,
    prompt: str,
    user_id: Optional[str],
    org_id: Optional[str],
    plan: Optional[str],
    explicit_profile_id: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """JSON-friendly wrapper around build_routing_result."""
    result = build_routing_result(
        prompt=prompt,
        user_id=user_id,
        org_id=org_id,
        plan=plan,
        explicit_profile_id=explicit_profile_id,
        extra_context=extra_context,
    )
    return result.to_dict()

