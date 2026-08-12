from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, List

from app.runtime.execution_graph.execution_graph_dag import build_execution_dag

MODE = "SHADOW_ONLY"

def _topological_levels(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    node_ids = [n["node_id"] for n in nodes]
    indegree = {n: 0 for n in node_ids}
    children = defaultdict(list)

    for e in edges:
        src = e["from"]
        dst = e["to"]
        children[src].append(dst)
        indegree[dst] += 1

    queue = deque([n for n in node_ids if indegree[n] == 0])
    levels = []
    visited = []

    while queue:
        current_level = list(queue)
        queue.clear()
        levels.append(current_level)

        for node_id in current_level:
            visited.append(node_id)
            for child in children[node_id]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)

    cycle_detected = len(visited) != len(node_ids)

    return {
        "levels": levels,
        "visited_count": len(visited),
        "cycle_detected": cycle_detected,
        "parallelizable_levels": [
            level for level in levels if len(level) > 1
        ],
    }

def plan_dependencies(query: str) -> Dict[str, Any]:
    dag = build_execution_dag(query)
    topology = _topological_levels(dag["nodes"], dag["edges"])

    node_lookup = {n["node_id"]: n for n in dag["nodes"]}

    execution_levels = []
    for idx, level in enumerate(topology["levels"], start=1):
        execution_levels.append({
            "level": idx,
            "node_ids": level,
            "nodes": [
                {
                    "node_id": node_id,
                    "node_type": node_lookup[node_id]["node_type"],
                    "label": node_lookup[node_id]["label"],
                    "uid": node_lookup[node_id]["uid"],
                    "mode": MODE,
                    "execution_allowed": False,
                    "production_allowed": False,
                }
                for node_id in level
            ],
            "can_run_parallel": len(level) > 1,
        })

    return {
        "mode": MODE,
        "query": query,
        "intent": dag["intent"],
        "node_count": dag["node_count"],
        "edge_count": dag["edge_count"],
        "cycle_detected": topology["cycle_detected"],
        "execution_levels_count": len(execution_levels),
        "execution_levels": execution_levels,
        "parallelizable_levels_count": len(topology["parallelizable_levels"]),
        "execution_allowed": False,
        "production_allowed": False,
        "shadow_only": True,
        "scheduler_ready": not topology["cycle_detected"],
        "final_authority_required": True,
    }

if __name__ == "__main__":
    import json

    tests = [
        "como automatizar confinamento de boi",
        "crie estratégia de marketing para eldora",
        "validar runtime trader FTMO paper only",
        "prossiga",
    ]

    for t in tests:
        print(json.dumps(plan_dependencies(t), indent=2, ensure_ascii=False))
