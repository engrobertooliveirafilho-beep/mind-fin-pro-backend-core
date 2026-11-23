"""R861: side-effect-free isolated replacement for original agents_runtime.py.

Original Drive ID: 10WByay5ageFVa7fDPGsF4s-6mg2DDTxT.
No scheduler import or start during module import. No file reads until explicit call.
"""
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
    return _build_generic_proposal("meta.autonomous_evolution_agent")

def generate_agent_blueprints_for_global_mapper() -> List[Dict[str, Any]]:
    return _build_generic_proposal("meta.global_agent_mapper")

def generate_archives_agent_proposals() -> List[Dict[str, Any]]:
    return _build_generic_proposal("meta.mind_archives_agent_mapper")

def start_scheduler(*args, **kwargs):
    """Explicit compatibility gate; never starts historical daemon."""
    return {"status": "blocked", "reason": "autonomous_scheduler_disabled",
            "executed": 0, "runtime_certified": False, "integration_authorized": False}
