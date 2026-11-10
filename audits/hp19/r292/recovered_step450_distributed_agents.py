from datetime import datetime
from typing import List, Dict, Any, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
router = APIRouter()
AgentRole = Literal["orchestrator", "toolmaster", "researcher", "analyzer", "planner"]
class ClusterConfig(BaseModel):
    cluster_id: str
    capacity: int = Field(..., ge=1)
    latency_ms: float = Field(..., ge=0.0)
class DistributedAgentConfig(BaseModel):
    agent_id: str
    role: AgentRole
    weight: float = Field(0.5, ge=0.0, le=1.0)
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
def _cluster_base_score(cluster: ClusterConfig, total_capacity: int) -> float:
    cap_ratio = cluster.capacity / total_capacity if total_capacity > 0 else 0.0
    latency_factor = 1.0 / (1.0 + (cluster.latency_ms / 100.0))
    return cap_ratio * latency_factor
@router.post("/run", response_model=DistributedResponse)
def run_distributed_agents(request: DistributedRequest) -> DistributedResponse:
    if not request.clusters or not request.agents:
        return DistributedResponse(task=request.task, assignments=[], stats={"clusters":len(request.clusters),"agents":len(request.agents),"fanout":request.fanout}, meta={"version":"step450-v1","created_at":datetime.utcnow().isoformat()+"Z","engine":"distributed_agents_step450"})
    total_capacity = sum(c.capacity for c in request.clusters) or 1
    cluster_scores = {c.cluster_id:_cluster_base_score(c,total_capacity) for c in request.clusters}
    assignments = []
    best_cluster_id = {a.agent_id:max(request.clusters,key=lambda c:cluster_scores[c.cluster_id]).cluster_id for a in request.agents}
    for agent in request.agents:
        base_cluster_id=best_cluster_id[agent.agent_id]
        base_score=cluster_scores[base_cluster_id]*(0.5+agent.weight)
        for shard in range(1,request.fanout+1):
            score=base_score*(1.0-(shard-1)*0.05)
            assignments.append(AgentAssignment(cluster_id=base_cluster_id,agent_id=agent.agent_id,role=agent.role,shard_index=shard,score=round(score,4),reason=f"best_cluster_for_agent (shard={shard})"))
    stats={"clusters":len(request.clusters),"agents":len(request.agents),"fanout":request.fanout,"assignments":len(assignments)}
    return DistributedResponse(task=request.task,assignments=assignments,stats=stats,meta={"version":"step450-v1","created_at":datetime.utcnow().isoformat()+"Z","engine":"distributed_agents_step450"})
