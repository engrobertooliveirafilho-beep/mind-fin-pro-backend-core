import json
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

OUT1 = Path("runtime/capability_merge/capability_merge_report.json")
OUT2 = Path("runtime/capability_merge/consolidation_plan.json")

SOURCES = [
    "app/runtime/universal_capability_registry.json",
    "runtime/knowledge_graph/drive_knowledge_graph.json",
    "runtime/reconstruction/capability_reconstruction_plan.json",
    "runtime/orphan_recovery/orphan_recovery_plan.json",
    "runtime/orphan_recovery/adapter_recovery_plan.json",
    "runtime/capability_map/absorbed_vs_pending_map.json",
]

def load(path):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": str(e)}

def norm(s):
    return str(s or "").lower().replace("_", " ").replace("-", " ").strip()

records = []

for src in SOURCES:
    data = load(src)
    if data is None:
        continue

    blob = json.dumps(data, ensure_ascii=False)

    if isinstance(data, dict):
        for key in ["absorbed", "pending"]:
            for item in data.get(key, []) if isinstance(data.get(key), list) else []:
                name = item.get("capability") or item.get("label") or key
                records.append({
                    "source": src,
                    "kind": key.upper(),
                    "name": name,
                    "normalized": norm(name),
                    "meta": item
                })

        for node in data.get("nodes", []) if isinstance(data.get("nodes"), list) else []:
            if node.get("type") in ["CAPABILITY", "PENDING_CAPABILITY", "MODULE", "TASK"]:
                name = node.get("label") or node.get("id")
                records.append({
                    "source": src,
                    "kind": node.get("type"),
                    "name": name,
                    "normalized": norm(name),
                    "meta": node
                })

        for task in data.get("tasks", []) if isinstance(data.get("tasks"), list) else []:
            mission = task.get("mission", {})
            name = task.get("task_id") or task.get("source_priority_id")
            records.append({
                "source": src,
                "kind": "TASK",
                "name": name,
                "normalized": norm(json.dumps(mission, ensure_ascii=False)[:160]),
                "meta": task
            })

        for item in data.get("orphans", []) if isinstance(data.get("orphans"), list) else []:
            name = item.get("recovery_id")
            records.append({
                "source": src,
                "kind": "ORPHAN",
                "name": name,
                "normalized": norm(name),
                "meta": item
            })

        for item in data.get("adapters", []) if isinstance(data.get("adapters"), list) else []:
            name = item.get("adapter_id")
            records.append({
                "source": src,
                "kind": "ADAPTER",
                "name": name,
                "normalized": norm(name),
                "meta": item
            })

groups = defaultdict(list)
for r in records:
    key_tokens = set(norm(r["name"]).split())
    base_key = " ".join(sorted([t for t in key_tokens if len(t) >= 4])[:4]) or r["normalized"]
    groups[base_key].append(r)

overlaps = []
for key, items in groups.items():
    if len(items) > 1:
        overlaps.append({
            "merge_group_id": f"MERGE-{len(overlaps)+1:03d}",
            "normalized_key": key,
            "status": "PENDING_REVIEW",
            "execution_allowed": False,
            "approval_required": True,
            "items_count": len(items),
            "items": items,
            "recommendation": "REVIEW_FOR_DUPLICATE_OR_OVERLAP"
        })

# Heurísticas institucionais para redundância funcional
semantic_clusters = {
    "retrieval_memory_context": ["retrieval", "memory", "context", "semantic"],
    "whatsapp_runtime": ["whatsapp", "runtime", "reply", "conversation"],
    "knowledge_capability_drive": ["knowledge", "capability", "drive", "graph"],
    "governance_execution": ["governance", "approval", "gate", "execution"],
    "orphan_adapter_recovery": ["orphan", "adapter", "recovery"]
}

semantic_overlaps = []
for cluster, terms in semantic_clusters.items():
    hits = []
    for r in records:
        hay = norm(r["name"]) + " " + norm(json.dumps(r.get("meta", {}), ensure_ascii=False))
        if any(t in hay for t in terms):
            hits.append(r)
    if len(hits) > 1:
        semantic_overlaps.append({
            "cluster": cluster,
            "status": "PENDING_REVIEW",
            "items_count": len(hits),
            "items": hits[:50],
            "recommendation": "CHECK_FUNCTIONAL_OVERLAP"
        })

merge_report = {
    "milestone": "P4.87 COMPLETE",
    "engine": "CAPABILITY_MERGE_ENGINE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "PLAN_ONLY",
    "governance": "P4.83_ENFORCED",
    "sources": SOURCES,
    "records_scanned": len(records),
    "exact_or_token_overlaps": len(overlaps),
    "semantic_overlap_clusters": len(semantic_overlaps),
    "overlaps": overlaps,
    "semantic_overlaps": semantic_overlaps,
    "next": "P4.88 TECHNICAL GAP DETECTOR"
}

consolidation_plan = {
    "milestone": "P4.87 COMPLETE",
    "plan": "CONSOLIDATION_PLAN",
    "mode": "PLAN_ONLY",
    "automatic_merge": "FORBIDDEN",
    "approval_required": True,
    "steps": [
        "review_overlap_groups",
        "select_canonical_capability",
        "map_redundant_modules",
        "define_adapter_or_deprecation_plan",
        "generate_tests_before_merge",
        "require_manual_approval",
        "execute_only_after_p483_unlock"
    ],
    "merge_candidates": overlaps,
    "semantic_clusters": semantic_overlaps
}

OUT1.write_text(json.dumps(merge_report, indent=2, ensure_ascii=False), encoding="utf-8")
OUT2.write_text(json.dumps(consolidation_plan, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.87 COMPLETE",
    "records_scanned": len(records),
    "overlap_groups": len(overlaps),
    "semantic_clusters": len(semantic_overlaps),
    "mode": "PLAN_ONLY",
    "next": "P4.88 TECHNICAL GAP DETECTOR"
}, indent=2, ensure_ascii=False))
