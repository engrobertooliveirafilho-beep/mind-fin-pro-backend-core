from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class CognitiveContext:
    schema_version: str
    mode: str
    generated_at: str
    user_id: Optional[str]
    relationship_memory: Dict[str, Any]
    goal_tracking: Dict[str, Any]
    digital_twin: Dict[str, Any]
    behavior_modeling: Dict[str, Any]
    emotional_continuity: Dict[str, Any]
    long_term_memory: Dict[str, Any]
    self_reflection: Dict[str, Any]
    live_cognition: Dict[str, Any]
    telemetry: Dict[str, Any]
    safety: Dict[str, Any]


def _safe_layer(name: str, value: Any) -> Dict[str, Any]:
    if value is None:
        return {"layer": name, "status": "missing", "data": {}}
    if isinstance(value, dict):
        return {"layer": name, "status": "ok", "data": value}
    return {"layer": name, "status": "ok", "data": {"value": value}}


def build_cognitive_context(
    *,
    user_id: Optional[str] = None,
    relationship_memory: Any = None,
    goal_tracking: Any = None,
    digital_twin: Any = None,
    behavior_modeling: Any = None,
    emotional_continuity: Any = None,
    long_term_memory: Any = None,
    self_reflection: Any = None,
    live_cognition: Any = None,
    source_context: Optional[Dict[str, Any]] = None,
    feature_flags: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    flags = feature_flags or {}

    ctx = CognitiveContext(
        schema_version="p19p39.v1",
        mode="SHADOW_ONLY",
        generated_at=datetime.now(timezone.utc).isoformat(),
        user_id=user_id,
        relationship_memory=_safe_layer("relationship_memory", relationship_memory),
        goal_tracking=_safe_layer("goal_tracking", goal_tracking),
        digital_twin=_safe_layer("digital_twin", digital_twin),
        behavior_modeling=_safe_layer("behavior_modeling", behavior_modeling),
        emotional_continuity=_safe_layer("emotional_continuity", emotional_continuity),
        long_term_memory=_safe_layer("long_term_memory", long_term_memory),
        self_reflection=_safe_layer("self_reflection", self_reflection),
        live_cognition=_safe_layer("live_cognition", live_cognition),
        telemetry={
            "builder": "cognitive_context_builder",
            "program": "P19P39",
            "shadow_only": True,
            "runtime_mutation": False,
            "response_mutation": False,
            "source_context_keys": sorted(list((source_context or {}).keys())),
        },
        safety={
            "feature_flagged": True,
            "enabled": bool(flags.get("P19P39_COGNITIVE_CONTEXT_ENABLED", False)),
            "default_enabled": False,
            "canary_ready": True,
            "rollbackable": True,
            "production_response_impact": "none",
        },
    )

    return {"cognitive_context": asdict(ctx)}


def attach_cognitive_context_shadow(
    ctx: Dict[str, Any],
    *,
    user_id: Optional[str] = None,
    feature_flags: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    base = dict(ctx or {})
    built = build_cognitive_context(
        user_id=user_id,
        relationship_memory=base.get("relationship_memory") or base.get("p19p36o_relationship_memory_shadow"),
        goal_tracking=base.get("goal_tracking") or base.get("p19p36p_goal_tracker_shadow"),
        digital_twin=base.get("digital_twin") or base.get("digital_twin_real"),
        behavior_modeling=base.get("behavior_modeling"),
        emotional_continuity=base.get("emotional_continuity") or base.get("emotional_continuity_real"),
        long_term_memory=base.get("long_term_memory") or base.get("long_term_memory_real"),
        self_reflection=base.get("self_reflection"),
        live_cognition=base.get("live_cognition"),
        source_context=base,
        feature_flags=feature_flags,
    )
    base.update(built)
    return base
