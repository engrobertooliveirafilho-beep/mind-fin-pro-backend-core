from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

AGENT_ID: str = "sec.sentinel"
AGENT_GROUP: str = "unknown"
AGENT_KIND: str = "vigilance_ai"
AGENT_NAME: str = "sec.sentinel"
STEP_IDS: List[int] = []
DESCRIPTION: str = """"""


def describe_capabilities() -> Dict[str, Any]:
    return {
        "id": AGENT_ID,
        "group": AGENT_GROUP,
        "kind": AGENT_KIND,
        "name": AGENT_NAME,
        "step_ids": STEP_IDS,
        "description": DESCRIPTION,
    }


def run_dry(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "agent_id": AGENT_ID,
        "status": "not_implemented",
        "mode": "stub",
        "received": payload or {},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

