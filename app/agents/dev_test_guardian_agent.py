from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

AGENT_ID: str = "dev.test_guardian_agent"
AGENT_GROUP: str = "dev"
AGENT_KIND: str = "test_impact_analyzer"
AGENT_NAME: str = "dev.test_guardian_agent"
STEP_IDS: List[int] = []
DESCRIPTION: str = """Analisa impacto em testes, sugere novos testes e garante que a suite não quebre."""


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

