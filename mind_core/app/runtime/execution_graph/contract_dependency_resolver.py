from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List

from app.runtime.knowledge_fusion.knowledge_fusion_engine import fuse_knowledge
from app.runtime.capability_identity.universal_capability_identity import resolve_capability

MODE = "SHADOW_ONLY"
ROOT = Path.cwd()
CONTRACTS = ROOT / "app/runtime/capability_contracts/capability_semantic_contracts.json"

ROLE_PROVIDES = {
    "auth_policy_and_tenant_guard": ["auth", "policy", "guard", "tenant", "user"],
    "semantic_memory_and_graph_access": ["semantic", "memory", "graph", "retrieve", "remember"],
    "runtime_health_supervision": ["runtime", "health", "supervisor", "self_heal"],
    "goal_planning_and_checkpointing": ["goal", "plan", "planner", "checkpoint"],
    "distributed_task_orchestration": ["task", "orchestration", "distributed", "async"],
}

ROLE_REQUIRES = {
    "auth_policy_and_tenant_guard": [],
    "semantic_memory_and_graph_access": ["auth", "tenant"],
    "runtime_health_supervision": ["auth"],
    "goal_planning_and_checkpointing": ["semantic", "runtime"],
    "distributed_task_orchestration": ["plan", "runtime"],
}

def _load_contracts() -> List[Dict[str, Any]]:
    if not CONTRACTS.exists():
        return []
    data = json.loads(CONTRACTS.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("contracts"), list):
        return data["contracts"]
    if isinstance(data, dict):
        return [v for v in data.values() if isinstance(v, dict)]
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []

def _norm_path(value: str) -> str:
    return str(value or "").replace("\\", "/").lower()

def _contract_for_file(file: str) -> Dict[str, Any] | None:
    wanted = _norm_path(file)
    for c in _load_contracts():
        p = _norm_path(c.get("path") or c.get("file") or "")
        if p == wanted or wanted.endswith(p) or p.endswith(wanted):
            return c
    return None

def _tokens_from_contract(step: Dict[str, Any]) -> Dict[str, List[str]]:
    role = step["role"]
    contract = _contract_for_file(step["file"]) or {}

    provides = set(ROLE_PROVIDES.get(role, []))
    requires = set(ROLE_REQUIRES.get(role, []))

    for x in contract.get("can_handle", []) or []:
        provides.add(str(x).lower())

    for x in contract.get("produces", []) or []:
        provides.add(str(x).lower())

    for x in contract.get("requires", []) or []:
        requires.add(str(x).lower())

    return {
        "requires": sorted(requires),
        "provides": sorted(provides),
        "contract_found": contract != {},
    }

def _topological_levels(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    ids = [n["node_id"] for n in nodes]
    indegree = {x: 0 for x in ids}
    children = defaultdict(list)

    for e in edges:
        children[e["from"]].append(e["to"])
        indegree[e["to"]] += 1

    q = deque([x for x in ids if indegree[x] == 0])
    levels = []
    visited = []

    while q:
        level = list(q)
        q.clear()
        levels.append(level)

        for node in level:
            visited.append(node)
            for child in children[node]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    q.append(child)

    return {
        "levels": levels,
        "cycle_detected": len(visited) != len(ids),
        "parallelizable_levels": [x for x in levels if len(x) > 1],
        "visited_count": len(visited),
    }

def resolve_contract_dependencies(query: str) -> Dict[str, Any]:
    fused = fuse_knowledge(query)

    nodes = [
        {"node_id": "N001_GOAL", "node_type": "GOAL", "label": query, "uid": None, "mode": MODE, "execution_allowed": False, "production_allowed": False},
        {"node_id": "N002_INTENT", "node_type": "INTENT", "label": fused["intent"], "uid": None, "mode": MODE, "execution_allowed": False, "production_allowed": False},
        {"node_id": "N003_KNOWLEDGE_FUSION", "node_type": "KNOWLEDGE", "label": "fused_shadow_knowledge", "uid": None, "mode": MODE, "execution_allowed": False, "production_allowed": False},
    ]

    edges = [
        {"from": "N001_GOAL", "to": "N002_INTENT", "mode": MODE, "execution_allowed": False, "production_allowed": False},
        {"from": "N002_INTENT", "to": "N003_KNOWLEDGE_FUSION", "mode": MODE, "execution_allowed": False, "production_allowed": False},
    ]

    cap_nodes = []
    for idx, step in enumerate(fused["fused_capability_chain"], start=4):
        resolved = resolve_capability(step["file"])
        contract_tokens = _tokens_from_contract(step)

        node = {
            "node_id": f"N{idx:03d}_{resolved['uid']}",
            "node_type": "CAPABILITY",
            "label": step["role"],
            "role": step["role"],
            "uid": resolved["uid"],
            "module": step["module"],
            "file": step["file"],
            "requires": contract_tokens["requires"],
            "provides": contract_tokens["provides"],
            "contract_found": contract_tokens["contract_found"],
            "mode": MODE,
            "execution_allowed": False,
            "production_allowed": False,
            "direct_user_response_allowed": False,
        }

        nodes.append(node)
        cap_nodes.append(node)

    # MIND_OS_46B_ORDERED_PROVIDER_DAG
    # A capability may consume contracts only from earlier stages.
    # This preserves the semantic chain as a directed acyclic graph.
    capability_order = {
        node["node_id"]: position
        for position, node in enumerate(cap_nodes)
    }

    for target in cap_nodes:
        matched = False
        target_position = capability_order[target["node_id"]]

        for req in target["requires"]:
            providers = [
                source for source in cap_nodes
                if capability_order[source["node_id"]] < target_position
                and req in source["provides"]
            ]

            for source in providers:
                edges.append({
                    "from": source["node_id"],
                    "to": target["node_id"],
                    "mode": MODE,
                    "execution_allowed": False,
                    "production_allowed": False,
                    "dependency_reason": f"contract_requires:{req}",
                })
                matched = True

        if not matched:
            edges.append({
                "from": "N003_KNOWLEDGE_FUSION",
                "to": target["node_id"],
                "mode": MODE,
                "execution_allowed": False,
                "production_allowed": False,
                "dependency_reason": "no_contract_dependency_matched",
            })

    qg_id = f"N{len(nodes)+1:03d}_QUALITY_GUARD"
    nodes.append({"node_id": qg_id, "node_type": "QUALITY_GUARD", "label": "quality_guard_required", "uid": None, "mode": MODE, "execution_allowed": False, "production_allowed": False})

    outgoing = defaultdict(int)
    for e in edges:
        outgoing[e["from"]] += 1

    for n in cap_nodes:
        if outgoing[n["node_id"]] == 0:
            edges.append({
                "from": n["node_id"],
                "to": qg_id,
                "mode": MODE,
                "execution_allowed": False,
                "production_allowed": False,
                "dependency_reason": "terminal_capability_to_quality_guard",
            })

    fa_id = f"N{len(nodes)+1:03d}_FINAL_AUTHORITY"
    nodes.append({"node_id": fa_id, "node_type": "FINAL_AUTHORITY", "label": "final_authority_required", "uid": None, "mode": MODE, "execution_allowed": False, "production_allowed": False})

    edges.append({
        "from": qg_id,
        "to": fa_id,
        "mode": MODE,
        "execution_allowed": False,
        "production_allowed": False,
        "dependency_reason": "quality_guard_to_final_authority",
    })

    topology = _topological_levels(nodes, edges)
    lookup = {n["node_id"]: n for n in nodes}

    levels = []
    for i, level in enumerate(topology["levels"], start=1):
        levels.append({
            "level": i,
            "node_ids": level,
            "can_run_parallel": len(level) > 1,
            "nodes": [lookup[x] for x in level],
        })

    missing_contracts = [n["node_id"] for n in cap_nodes if not n["contract_found"]]

    return {
        "mode": MODE,
        "query": query,
        "intent": fused["intent"],
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "execution_levels": levels,
        "execution_levels_count": len(levels),
        "parallelizable_levels_count": len(topology["parallelizable_levels"]),
        "cycle_detected": topology["cycle_detected"],
        "scheduler_ready": not topology["cycle_detected"],
        "missing_contracts": missing_contracts,
        "missing_contracts_count": len(missing_contracts),
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
        print(json.dumps(resolve_contract_dependencies(q), indent=2, ensure_ascii=False))
