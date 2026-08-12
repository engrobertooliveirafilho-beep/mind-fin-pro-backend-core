from __future__ import annotations

from typing import Any, Dict, List
from collections import defaultdict, deque

from app.runtime.knowledge_fusion.knowledge_fusion_engine import fuse_knowledge
from app.runtime.capability_identity.universal_capability_identity import resolve_capability

MODE = "SHADOW_ONLY"

DEPENDENCY_RULES = {
    "auth_policy_and_tenant_guard": [],
    "semantic_memory_and_graph_access": ["auth_policy_and_tenant_guard"],
    "runtime_health_supervision": ["auth_policy_and_tenant_guard"],
    "goal_planning_and_checkpointing": [
        "semantic_memory_and_graph_access",
        "runtime_health_supervision",
    ],
    "distributed_task_orchestration": [
        "goal_planning_and_checkpointing",
        "runtime_health_supervision",
    ],
}

def _topological_levels(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    node_ids = [n["node_id"] for n in nodes]
    indegree = {n: 0 for n in node_ids}
    children = defaultdict(list)

    for e in edges:
        children[e["from"]].append(e["to"])
        indegree[e["to"]] += 1

    queue = deque([n for n in node_ids if indegree[n] == 0])
    levels = []
    visited = []

    while queue:
        current = list(queue)
        queue.clear()
        levels.append(current)

        for node_id in current:
            visited.append(node_id)
            for child in children[node_id]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)

    return {
        "levels": levels,
        "cycle_detected": len(visited) != len(node_ids),
        "parallelizable_levels": [x for x in levels if len(x) > 1],
        "visited_count": len(visited),
    }

def infer_dependency_dag(query: str) -> Dict[str, Any]:
    fused = fuse_knowledge(query)

    nodes = [
        {
            "node_id": "N001_GOAL",
            "node_type": "GOAL",
            "label": query,
            "uid": None,
            "role": None,
            "mode": MODE,
            "execution_allowed": False,
            "production_allowed": False,
        },
        {
            "node_id": "N002_INTENT",
            "node_type": "INTENT",
            "label": fused["intent"],
            "uid": None,
            "role": None,
            "mode": MODE,
            "execution_allowed": False,
            "production_allowed": False,
        },
        {
            "node_id": "N003_KNOWLEDGE_FUSION",
            "node_type": "KNOWLEDGE",
            "label": "fused_shadow_knowledge",
            "uid": None,
            "role": None,
            "mode": MODE,
            "execution_allowed": False,
            "production_allowed": False,
        },
    ]

    edges = [
        {"from": "N001_GOAL", "to": "N002_INTENT", "mode": MODE, "execution_allowed": False, "production_allowed": False},
        {"from": "N002_INTENT", "to": "N003_KNOWLEDGE_FUSION", "mode": MODE, "execution_allowed": False, "production_allowed": False},
    ]

    role_to_node = {}

    for idx, step in enumerate(fused["fused_capability_chain"], start=4):
        resolved = resolve_capability(step["file"])
        uid = resolved["uid"]
        role = step["role"]
        node_id = f"N{idx:03d}_{uid}"

        role_to_node[role] = node_id

        nodes.append({
            "node_id": node_id,
            "node_type": "CAPABILITY",
            "label": role,
            "uid": uid,
            "role": role,
            "module": step["module"],
            "file": step["file"],
            "mode": MODE,
            "execution_allowed": False,
            "production_allowed": False,
            "direct_user_response_allowed": False,
        })

    capability_roles = list(role_to_node.keys())

    for role, node_id in role_to_node.items():
        required_roles = [
            r for r in DEPENDENCY_RULES.get(role, [])
            if r in role_to_node
        ]

        if required_roles:
            for dep_role in required_roles:
                edges.append({
                    "from": role_to_node[dep_role],
                    "to": node_id,
                    "mode": MODE,
                    "execution_allowed": False,
                    "production_allowed": False,
                    "dependency_reason": f"{role}_requires_{dep_role}",
                })
        else:
            edges.append({
                "from": "N003_KNOWLEDGE_FUSION",
                "to": node_id,
                "mode": MODE,
                "execution_allowed": False,
                "production_allowed": False,
                "dependency_reason": "root_capability_after_knowledge",
            })

    qg_id = f"N{len(nodes)+1:03d}_QUALITY_GUARD"
    nodes.append({
        "node_id": qg_id,
        "node_type": "QUALITY_GUARD",
        "label": "quality_guard_required",
        "uid": None,
        "role": None,
        "mode": MODE,
        "execution_allowed": False,
        "production_allowed": False,
    })

    terminal_caps = []
    outgoing = defaultdict(int)
    for e in edges:
        outgoing[e["from"]] += 1

    for role, node_id in role_to_node.items():
        if outgoing[node_id] == 0:
            terminal_caps.append(node_id)

    for node_id in terminal_caps:
        edges.append({
            "from": node_id,
            "to": qg_id,
            "mode": MODE,
            "execution_allowed": False,
            "production_allowed": False,
            "dependency_reason": "terminal_capability_to_quality_guard",
        })

    fa_id = f"N{len(nodes)+1:03d}_FINAL_AUTHORITY"
    nodes.append({
        "node_id": fa_id,
        "node_type": "FINAL_AUTHORITY",
        "label": "final_authority_required",
        "uid": None,
        "role": None,
        "mode": MODE,
        "execution_allowed": False,
        "production_allowed": False,
    })

    edges.append({
        "from": qg_id,
        "to": fa_id,
        "mode": MODE,
        "execution_allowed": False,
        "production_allowed": False,
        "dependency_reason": "quality_guard_to_final_authority",
    })

    topology = _topological_levels(nodes, edges)
    node_lookup = {n["node_id"]: n for n in nodes}

    execution_levels = []
    for i, level in enumerate(topology["levels"], start=1):
        execution_levels.append({
            "level": i,
            "node_ids": level,
            "can_run_parallel": len(level) > 1,
            "nodes": [node_lookup[x] for x in level],
        })

    return {
        "mode": MODE,
        "query": query,
        "intent": fused["intent"],
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "execution_levels": execution_levels,
        "execution_levels_count": len(execution_levels),
        "parallelizable_levels_count": len(topology["parallelizable_levels"]),
        "cycle_detected": topology["cycle_detected"],
        "scheduler_ready": not topology["cycle_detected"],
        "execution_allowed": False,
        "production_allowed": False,
        "shadow_only": True,
        "final_authority_required": True,
    }

if __name__ == "__main__":
    import json
    for q in [
        "como automatizar confinamento de boi",
        "crie estratégia de marketing para eldora",
        "validar runtime trader FTMO paper only",
        "prossiga",
    ]:
        print(json.dumps(infer_dependency_dag(q), indent=2, ensure_ascii=False))
