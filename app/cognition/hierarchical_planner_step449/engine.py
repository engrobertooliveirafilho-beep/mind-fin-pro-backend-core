from datetime import datetime
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
    descriptions = _build_level_descriptions(goal, context)
    nodes: List[HierarchyNode] = []
    node_counter = 0

    def add_node(level: int, parent_id: Optional[str], suffix: str, order: int) -> str:
        nonlocal node_counter
        node_counter += 1
        node_id = f"n{node_counter}"
        desc = f"{descriptions[level]} [{suffix}]"
        nodes.append(
            HierarchyNode(
                node_id=node_id,
                parent_id=parent_id,
                level=level,
                description=desc,
                order=order,
            )
        )
        return node_id

    # Nível 1: um nó raiz
    root_id = add_node(level=1, parent_id=None, suffix="visao_geral", order=1)

    if depth >= 2:
        # Nível 2: 3 blocos principais
        fronts = ["produto", "go_to_market", "risco_governanca"]
        front_ids: List[str] = []
        for idx, f in enumerate(fronts, start=1):
            fid = add_node(level=2, parent_id=root_id, suffix=f, order=idx)
            front_ids.append(fid)

        if depth >= 3:
            # Nível 3: 2 tarefas por frente
            for fid in front_ids:
                add_node(level=3, parent_id=fid, suffix="design_execucao", order=1)
                add_node(level=3, parent_id=fid, suffix="monitorar_kpis", order=2)

    return nodes


@router.post("/plan", response_model=HierarchicalPlanResponse)
def plan_hierarchy(request: HierarchicalPlanRequest) -> HierarchicalPlanResponse:
    depth = max(1, min(request.depth, 3))
    nodes = _build_nodes(request.goal, depth, request.context)

    snapshot = {
        "memory_key": request.memory_key or f"hp-{abs(hash(request.goal)) % 10_000}",
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
            "created_at": datetime.utcnow().isoformat() + "Z",
            "engine": "hierarchical_planner_step449",
        },
    )

