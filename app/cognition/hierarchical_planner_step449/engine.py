from datetime import datetime, timezone
from hashlib import sha256
from typing import List, Dict, Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class HierarchyNode(BaseModel):
    node_id: str
    parent_id: Optional[str]
    level: int = Field(..., ge=1, le=3)
    description: str
    order: int


class HierarchicalPlanRequest(BaseModel):
    goal: str
    depth: int = Field(3, ge=1, le=3)
    memory_key: Optional[str] = None
    context: Optional[str] = None


class HierarchicalPlanResponse(BaseModel):
    goal: str
    depth: int
    nodes: List[HierarchyNode]
    memory_snapshot: Dict[str, Any]
    meta: Dict[str, Any]


def _build_level_descriptions(goal: str, context: Optional[str]) -> Dict[int, str]:
    base = goal.strip()
    ctx_snip = f" | ctx: {context[:60]}" if context else ""
    return {
        1: f"MACRO: {base}{ctx_snip}",
        2: f"BLOCOS: decompor '{base}' em frentes executaveis.",
        3: f"TAREFAS: passos operacionais para entregar '{base}'.",
    }


def _build_nodes(goal: str, depth: int, context: Optional[str]) -> List[HierarchyNode]:
    from app.planning.hierarchical_planner import HierarchicalPlanner

    plan = HierarchicalPlanner().build_plan(
        goal=goal, horizon_steps=6, memory_summary=context
    )
    nodes = []
    for step in plan.steps:
        if step.level + 1 <= depth:
            nodes.append(HierarchyNode(
                node_id=step.id, parent_id=step.parent_id,
                level=step.level + 1, description=step.description,
                order=len(nodes) + 1,
            ))
    return nodes


@router.post("/plan", response_model=HierarchicalPlanResponse)
def plan_hierarchy(request: HierarchicalPlanRequest) -> HierarchicalPlanResponse:
    if not request.goal.strip():
        raise ValueError("goal required")
    depth = request.depth
    nodes = _build_nodes(request.goal, depth, request.context)

    snapshot = {
        "memory_key": request.memory_key or "hp-" + sha256(request.goal.encode("utf-8")).hexdigest(),
        "nodes_count": len(nodes),
        "depth": depth,
    }

    return HierarchicalPlanResponse(
        goal=request.goal,
        depth=depth,
        nodes=nodes,
        memory_snapshot=snapshot,
        meta={
            "version": "step449-v1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "engine": "hierarchical_planner_step449",
        },
    )

