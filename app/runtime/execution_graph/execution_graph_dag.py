from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from app.runtime.knowledge_fusion.knowledge_fusion_engine import fuse_knowledge
from app.runtime.capability_identity.universal_capability_identity import resolve_capability

MODE = "SHADOW_ONLY"

@dataclass(frozen=True)
class DAGNode:
    node_id: str
    node_type: str
    label: str
    uid: str | None
    module: str | None
    file: str | None
    depends_on: List[str]
    mode: str
    production_allowed: bool
    execution_allowed: bool
    direct_user_response_allowed: bool

def _node(
    node_id: str,
    node_type: str,
    label: str,
    depends_on: List[str] | None = None,
    uid: str | None = None,
    module: str | None = None,
    file: str | None = None,
) -> DAGNode:
    return DAGNode(
        node_id=node_id,
        node_type=node_type,
        label=label,
        uid=uid,
        module=module,
        file=file,
        depends_on=depends_on or [],
        mode=MODE,
        production_allowed=False,
        execution_allowed=False,
        direct_user_response_allowed=False,
    )

def build_execution_dag(query: str) -> Dict[str, Any]:
    fused = fuse_knowledge(query)

    nodes: List[DAGNode] = [
        _node("N001_GOAL", "GOAL", query),
        _node("N002_INTENT", "INTENT", fused["intent"], ["N001_GOAL"]),
        _node("N003_KNOWLEDGE_FUSION", "KNOWLEDGE", "fused_shadow_knowledge", ["N002_INTENT"]),
    ]

    previous = "N003_KNOWLEDGE_FUSION"

    for idx, step in enumerate(fused["fused_capability_chain"], start=1):
        resolved = resolve_capability(step["file"])
        uid = resolved["uid"]

        node_id = f"N{idx+3:03d}_{uid}"
        nodes.append(
            _node(
                node_id=node_id,
                node_type="CAPABILITY",
                label=step["role"],
                depends_on=[previous],
                uid=uid,
                module=step["module"],
                file=step["file"],
            )
        )
        previous = node_id

    qg_id = f"N{len(nodes)+1:03d}_QUALITY_GUARD"
    nodes.append(_node(qg_id, "QUALITY_GUARD", "quality_guard_required", [previous]))

    fa_id = f"N{len(nodes)+1:03d}_FINAL_AUTHORITY"
    nodes.append(_node(fa_id, "FINAL_AUTHORITY", "final_authority_required", [qg_id]))

    edges = []
    for n in nodes:
        for dep in n.depends_on:
            edges.append({
                "from": dep,
                "to": n.node_id,
                "mode": MODE,
                "execution_allowed": False,
                "production_allowed": False,
            })

    return {
        "mode": MODE,
        "query": query,
        "intent": fused["intent"],
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": [asdict(n) for n in nodes],
        "edges": edges,
        "is_dag": True,
        "execution_allowed": False,
        "production_allowed": False,
        "shadow_only": True,
        "final_authority_required": True,
    }

if __name__ == "__main__":
    tests = [
        "como automatizar confinamento de boi",
        "crie estratégia de marketing para eldora",
        "validar runtime trader FTMO paper only",
        "prossiga",
    ]

    for t in tests:
        print(json.dumps(build_execution_dag(t), indent=2, ensure_ascii=False))
