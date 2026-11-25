from datetime import datetime, timezone
from typing import List, Dict, Any, Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .allocator import allocate

router = APIRouter()
AgentRole = Literal['orchestrator', 'toolmaster', 'researcher', 'analyzer', 'planner']

class ClusterConfig(BaseModel):
    cluster_id: str
    capacity: int = Field(..., ge=1)
    latency_ms: float = Field(..., ge=0, allow_inf_nan=False)

class DistributedAgentConfig(BaseModel):
    agent_id: str
    role: AgentRole
    weight: float = Field(0.5, ge=0, le=1, allow_inf_nan=False)

class DistributedRequest(BaseModel):
    task: str
    clusters: List[ClusterConfig]
    agents: List[DistributedAgentConfig]
    fanout: int = Field(2, ge=1, le=10)

class AgentAssignment(BaseModel):
    cluster_id: str
    agent_id: str
    role: AgentRole
    shard_index: int
    score: float
    reason: str

class DistributedResponse(BaseModel):
    task: str
    assignments: List[AgentAssignment]
    stats: Dict[str, Any]
    meta: Dict[str, Any]

@router.post('/run', response_model=DistributedResponse)
def run_distributed_agents(request: DistributedRequest) -> DistributedResponse:
    try:
        plan = allocate(request.clusters, request.agents, request.fanout)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    clusters = {c.cluster_id: c for c in request.clusters}
    agents = {a.agent_id: a for a in request.agents}
    total = sum(c.capacity for c in request.clusters) or 1
    assignments = []
    for cid, aid, shard in plan:
        c, a = clusters[cid], agents[aid]
        score = c.capacity / total / (1 + c.latency_ms / 100) * (0.5 + a.weight) * (1 - (shard - 1) * 0.05)
        assignments.append(AgentAssignment(cluster_id=cid, agent_id=aid, role=a.role, shard_index=shard, score=round(score, 4), reason='capacity_aware'))
    demand = len(agents) * request.fanout
    return DistributedResponse(task=request.task, assignments=assignments, stats={'clusters': len(clusters), 'agents': len(agents), 'fanout': request.fanout, 'assignments': len(plan), 'requested': demand, 'unassigned': demand-len(plan)}, meta={'version': 'step450-v1', 'created_at': datetime.now(timezone.utc).isoformat(), 'engine': 'distributed_agents_step450', 'execution': 'PLAN_ONLY'})
