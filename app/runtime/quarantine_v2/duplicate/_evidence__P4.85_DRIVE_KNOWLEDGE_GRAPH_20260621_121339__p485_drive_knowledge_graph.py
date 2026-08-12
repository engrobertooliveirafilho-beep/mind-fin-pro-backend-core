import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(".")
OUT = Path("runtime/knowledge_graph/drive_knowledge_graph.json")

SOURCES = [
    "runtime/capacity_audit/project_state_audit.json",
    "runtime/capability_map/absorbed_vs_pending_map.json",
    "runtime/reconstruction/capability_reconstruction_plan.json",
    "runtime/prioritization/runtime_prioritized_queue.json",
    "app/runtime/universal_capability_registry.json",
]

nodes = {}
edges = []

def add_node(node_id, node_type, label, meta=None):
    nodes[node_id] = {
        "id": node_id,
        "type": node_type,
        "label": label,
        "meta": meta or {}
    }

def add_edge(src, dst, rel, meta=None):
    edges.append({
        "source": src,
        "target": dst,
        "relationship": rel,
        "meta": meta or {}
    })

def safe_json(path):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": str(e)}

add_node("PROJECT:MIND", "PROJECT", "MIND Platform")
add_node("PROJECT:ELDORA", "PROJECT", "Eldora Runtime")
add_edge("PROJECT:MIND", "PROJECT:ELDORA", "CONTAINS")

for src in SOURCES:
    data = safe_json(src)
    if data is None:
        continue

    doc_id = "DOC:" + src.replace("\\", "/")
    add_node(doc_id, "DOCUMENT", src, {"path": src})
    add_edge("PROJECT:MIND", doc_id, "HAS_DOCUMENT")

    if "absorbed" in data:
        for cap in data.get("absorbed", []):
            cid = "CAPABILITY:" + cap.get("capability", "unknown")
            add_node(cid, "CAPABILITY", cap.get("capability", "unknown"), cap)
            add_edge(doc_id, cid, "DESCRIBES")
            add_edge("PROJECT:MIND", cid, "HAS_CAPABILITY")

    if "pending" in data:
        for cap in data.get("pending", []):
            cid = "PENDING:" + cap.get("capability", "unknown")
            add_node(cid, "PENDING_CAPABILITY", cap.get("capability", "unknown"), cap)
            add_edge(doc_id, cid, "DESCRIBES")
            add_edge("PROJECT:MIND", cid, "HAS_PENDING_CAPABILITY")

    if "technical_gaps" in data:
        for gap in data.get("technical_gaps", []):
            gid = "GAP:" + gap.get("gap", "unknown")
            add_node(gid, "TECHNICAL_GAP", gap.get("gap", "unknown"), gap)
            add_edge(doc_id, gid, "IDENTIFIES")
            add_edge("PROJECT:MIND", gid, "HAS_GAP")

    if "tasks" in data:
        for task in data.get("tasks", []):
            tid = "TASK:" + task.get("task_id", task.get("source_priority_id", "unknown"))
            add_node(tid, "TASK", task.get("task_id", "task"), task)
            add_edge(doc_id, tid, "GENERATES")
            add_edge("PROJECT:MIND", tid, "HAS_TASK")

            recon = task.get("reconstruction", {})
            for f in recon.get("target_files", []):
                fid = "MODULE:" + f
                add_node(fid, "MODULE", f, {"path": f})
                add_edge(tid, fid, "TARGETS_FILE")

            for t in recon.get("target_tests", []):
                test_id = "TEST:" + t
                add_node(test_id, "TEST", t, {"path": t})
                add_edge(tid, test_id, "VALIDATED_BY")

            for d in recon.get("dependencies", []):
                dep_id = "DEPENDENCY:" + d
                add_node(dep_id, "DEPENDENCY", d, {"path": d})
                add_edge(tid, dep_id, "DEPENDS_ON")

graph = {
    "milestone": "P4.85 COMPLETE",
    "graph": "DRIVE_KNOWLEDGE_GRAPH",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "LOCAL_ARTIFACT_GRAPH",
    "drive_live_access": "NOT_REQUIRED_FOR_THIS_STAGE",
    "nodes_count": len(nodes),
    "edges_count": len(edges),
    "node_types": sorted(set(n["type"] for n in nodes.values())),
    "edge_types": sorted(set(e["relationship"] for e in edges)),
    "nodes": list(nodes.values()),
    "edges": edges,
    "next": "P4.86 ORPHAN RECOVERY ENGINE"
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.85 COMPLETE",
    "nodes": graph["nodes_count"],
    "edges": graph["edges_count"],
    "output": str(OUT),
    "next": graph["next"]
}, indent=2, ensure_ascii=False))
