from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

AGENT_ID: str = "domain.economics_finance_markets"
AGENT_GROUP: str = "domain"
AGENT_KIND: str = "finance_strategist"
AGENT_NAME: str = "Economics, Finance & Markets Agent"
STEP_IDS: List[int] = [124, 136, 139, 154, 170, 177, 190, 210, 211, 239, 281, 497, 498]
DESCRIPTION: str = """Especializado em economia, financas e mercados (incluindo bolsa), focado em cenarios, risco, alavancagem e impacto nos planos da MIND."""


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

