from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.modules.multi_agent_cognitive_generalist.engine import orchestrator

router = APIRouter()


class MultiAgentRunRequest(BaseModel):
    goal: str = Field(..., description="Objetivo cognitivo principal a ser trabalhado pelos agentes.")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contexto adicional (ex: cliente, horizonte, restrições).",
    )


@router.get("/ai/multi-agent/capabilities")
def get_multi_agent_capabilities():
    caps = orchestrator.capabilities()
    return {
        "meta": {
            "version": "step519-v1-hp19",
            "engine": "multi_agent_cognitive_generalist",
            "mode": "capabilities",
        },
        "capabilities": caps,
    }


@router.get("/ai/multi-agent/dry-run")
def dry_run_multi_agent():
    plan = orchestrator.dry_run()
    return {
        "meta": {
            "version": "step519-v1-hp19",
            "engine": "multi_agent_cognitive_generalist",
            "mode": "dry-run",
        },
        "plan": plan,
    }


@router.post("/ai/multi-agent/run")
def run_multi_agent(req: MultiAgentRunRequest):
    plan = orchestrator.run(req.goal, context=req.context or {})
    return {
        "meta": {
            "version": "step519-v1-hp19",
            "engine": "multi_agent_cognitive_generalist",
            "mode": "plan",
        },
        "plan": plan,
    }
