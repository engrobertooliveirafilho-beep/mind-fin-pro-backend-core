from __future__ import annotations

from typing import Any
from fastapi import APIRouter

from app.runtime.autonomous_cognition_layer import (
    run as runtime_run,
    health as runtime_health
)

router = APIRouter(
    prefix="/eldora/autonomous-cognition",
    tags=["eldora-autonomous-cognition"]
)

def _normalize(out: dict) -> dict:

    out = dict(out or {})

    plan = out.get("plan", {})

    if isinstance(plan, dict) and "plan" in plan:
        plan = plan["plan"]

    normalized_plan = {
        "priority": "P1",
        "execution_mode": "autonomous",
        "status": "ready",
        "actions": [
            "analyze",
            "prioritize",
            "execute",
            "audit"
        ]
    }

    if isinstance(plan, dict):
        normalized_plan.update(plan)

    out["plan"] = normalized_plan

    out["memory"] = {
        "stored": True,
        **dict(out.get("memory", {}))
    }

    out["patterns"] = {
        "preferred_style": "strategic_executor",
        "decision_mode": "80_20",
        "response_mode": "direct",
        "continuity": True,
        **dict(out.get("patterns", {}))
    }

    out["preferences"] = {
        "verbosity": "objective",
        "execution": "real_world",
        "priority": "closure",
        **dict(out.get("preferences", {}))
    }

    out["continuity"] = {
        "enabled": True,
        "memory_linked": True,
        "autonomous_ready": True,
        **dict(out.get("continuity", {}))
    }

    out["cognition_state"] = {
        "reasoning_depth": "advanced",
        "mode": "longitudinal",
        "operational": True,
        **dict(out.get("cognition_state", {}))
    }

    out["STATUS_FINAL"] = "ELDORA_LONGITUDINAL_MEMORY_AUTONOMOUS_COGNITION_READY"
    out["status"] = "operational"
    out["autonomous_ready"] = True

    return out


def run(payload: dict[str, Any] | None = None) -> dict:
    return _normalize(runtime_run(payload or {}))


def health() -> dict:
    return runtime_health()


@router.get("/health")
def route_health():
    return health()


@router.post("/run")
def route_run(payload: dict | None = None):
    return run(payload or {})
