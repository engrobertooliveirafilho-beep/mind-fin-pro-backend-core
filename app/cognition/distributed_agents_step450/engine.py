from datetime import datetime, timezone
from typing import List, Dict, Any, Literal
from math import isfinite

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

AgentRole = Literal["orchestrator", "toolmaster", "researcher", "analyzer", "planner"]


class ClusterConfig(BaseModel):
    cluster_id: str = Field(..., min_length=1, max_length=128)
    capacity: int = Field(..., ge=1)
    latency_ms: float = Field(..., ge=0.0)


class DistributedAgentConfig(BaseModel):
    agent_id: str = Field(..., min_length=1, max_length=128)
    role: AgentRole
    weight: float = Field(0.5, ge=0.0, le=1.0)


class DistributedRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=4096)
    clusters: List[ClusterConfig] = Field(..., min_length=1, max_length=128)
    agents: List[DistributedAgentConfig] = Field(..., min_length=1, max_length=128)
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


def _cluster_base_score(cluster: ClusterConfig, total_capacity: int) -> float:
    cap_ratio = cluster.capacity / total_capacity if total_capacity > 0 else 0.0
    latency_factor = 1.0 / (1.0 + (cluster.latency_ms / 100.0))
    return cap_ratio * latency_factor


@router.post("/run", response_model=DistributedResponse)
def run_distributed_agents(request: DistributedRequest) -> DistributedResponse:
    if not request.clusters or not request.agents:
        return DistributedResponse(
            task=request.task,
            assignments=[],
            stats={
                "clusters": len(request.clusters),
                "agents": len(request.agents),
                "fanout": request.fanout,
            },
            meta={
                "version": "step450-v1",
                "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
                "engine": "distributed_agents_step450",
            },
        )

    if len({c.cluster_id for c in request.clusters}) != len(request.clusters):
        raise HTTPException(status_code=422, detail='duplicate cluster_id')
    if len({a.agent_id for a in request.agents}) != len(request.agents):
        raise HTTPException(status_code=422, detail='duplicate agent_id')
    if any(not isfinite(c.latency_ms) for c in request.clusters) or any(not isfinite(a.weight) for a in request.agents):
        raise HTTPException(status_code=422, detail='nonfinite metrics')
    total_capacity = sum(c.capacity for c in request.clusters) or 1
    cluster_scores: Dict[str, float] = {
        c.cluster_id: _cluster_base_score(c, total_capacity)
        for c in request.clusters
    }

    assignments: List[AgentAssignment] = []

    # Para cada agente, atribui sempre ao melhor cluster (maior score base),
    # replicando em ate anout shards logicos.
    best_cluster_id = {
        a.agent_id: max(request.clusters, key=lambda c: cluster_scores[c.cluster_id]).cluster_id
        for a in request.agents
    }

    for agent in request.agents:
        base_cluster_id = best_cluster_id[agent.agent_id]
        base_score = cluster_scores[base_cluster_id] * (0.5 + agent.weight)
        for shard in range(1, request.fanout + 1):
            score = base_score * (1.0 - (shard - 1) * 0.05)
            assignments.append(
                AgentAssignment(
                    cluster_id=base_cluster_id,
                    agent_id=agent.agent_id,
                    role=agent.role,
                    shard_index=shard,
                    score=round(score, 4),
                    reason=f"best_cluster_for_agent (shard={shard})",
                )
            )

    stats = {
        "clusters": len(request.clusters),
        "agents": len(request.agents),
        "fanout": request.fanout,
        "assignments": len(assignments),
    }

    return DistributedResponse(
        task=request.task,
        assignments=assignments,
        stats=stats,
        meta={
            "version": "step450-v1",
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
            "engine": "distributed_agents_step450",
        },
    )

