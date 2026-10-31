from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

REG_PATH = Path(__file__).resolve().parent / "agents_registry.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_agents_registry() -> Dict[str, Any]:
    if not REG_PATH.exists():
        return {"agents": []}
    with REG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_agents() -> List[Dict[str, Any]]:
    data = load_agents_registry()
    agents = data.get("agents", [])
    if not isinstance(agents, list):
        return []
    return agents


def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    for agent in list_agents():
        if agent.get("id") == agent_id:
            return agent
    return None


def _build_generic_proposal(agent_id: str) -> List[Dict[str, Any]]:
    agent = get_agent(agent_id)
    if not agent:
        return []

    artifacts = agent.get("artifacts_produced") or {}
    fields = artifacts.get("fields") or []
    proposal_type = artifacts.get("proposal_type", "generic_proposal")

    base = {field: None for field in fields}
    base["__proposal_type"] = proposal_type
    base["__agent_id"] = agent_id
    base["generated_at"] = _now_iso()
    base["source"] = "registry_scan_minimal"

    return [base]


def generate_step_proposals_for_evolution_agent() -> List[Dict[str, Any]]:
    """Meta.autonomous_evolution_agent → propostas estruturais de STEP (mínimas, seguras)."""
    return _build_generic_proposal("meta.autonomous_evolution_agent")


def generate_agent_blueprints_for_global_mapper() -> List[Dict[str, Any]]:
    """Meta.global_agent_mapper → blueprints genéricos de agentes, baseado no registry."""
    return _build_generic_proposal("meta.global_agent_mapper")


def generate_archives_agent_proposals() -> List[Dict[str, Any]]:
    """Meta.mind_archives_agent_mapper → propostas derivadas de arquivos/visões (placeholder)."""
    return _build_generic_proposal("meta.mind_archives_agent_mapper")


# AUTO-HOOK: iniciar scheduler
try:
    from app.meta.agents_scheduler import start_scheduler
    start_scheduler()
except Exception:
    pass

