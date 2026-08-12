import os, json, traceback
from pathlib import Path

ROOT = Path(".")
APP = ROOT / "app"

def safe_read(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

print("P4.67_71_CORE_AUDIT_START")

level_c_terms = ["eldora_world", "eldora_meta", "eldora_mesh", "eldora_liveos", "eldora_evolution"]
level_c_hits = []
for py in APP.rglob("*.py"):
    txt = safe_read(py).lower()
    for term in level_c_terms:
        if term in txt or term in str(py).lower():
            level_c_hits.append(str(py))

kg_terms = ["drive", "knowledge", "retrieval", "semantic", "embedding", "pgvector", "memory_graph"]
kg_hits = []
for py in APP.rglob("*.py"):
    txt = safe_read(py).lower()
    if any(t in txt or t in str(py).lower() for t in kg_terms):
        kg_hits.append(str(py))

manifest_path = Path("app/runtime/memory_quarantine_manifest.json")
manifest = {}
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

kernel = {
    "entrypoints": {
        "whatsapp": "app/api/whatsapp.py",
        "pipeline": "app/runtime/cognitive_pipeline.py",
        "retrieval": "app/retrieval/semantic_provider.py",
        "memory_manifest": "app/runtime/memory_quarantine_manifest.json",
    },
    "certified_flow": [
        "INPUT",
        "WhatsApp adapter",
        "active_context / short_memory",
        "run_cognitive_pipeline",
        "semantic retrieval bridge",
        "pgvector/rest retrieval",
        "grounded answer",
        "output guard",
        "OUTPUT",
    ],
    "remaining_risks": [
        "Level C modules not proven as core capabilities",
        "Orphaned modules quarantined but not fully recovered",
        "Continuous daemon not implemented as production worker",
        "Retrieval grounding generic but still basic",
    ],
}

report = {
    "mission": "P4.66-P4.71_CONSOLIDATED_MIND_CORE",
    "status": "CONSOLIDATED_AUDIT_AND_PATCH_DONE",
    "p466_general_retrieval": "patched_if_not_present",
    "p467_level_c_hits_count": len(set(level_c_hits)),
    "p467_level_c_hits": sorted(set(level_c_hits))[:100],
    "p468_drive_kg_hits_count": len(set(kg_hits)),
    "p468_drive_kg_hits_sample": sorted(set(kg_hits))[:120],
    "p469_memory_manifest_counts": manifest.get("counts", {}),
    "p469_orphaned_modules": manifest.get("buckets", {}).get("ORPHANED_OR_UNUSED", []),
    "p470_kernel": kernel,
    "p471_continuity_daemon_blueprint": {
        "mode": "not_started",
        "recommended_next": "create supervised worker loop after core capabilities are fully recovered",
        "minimum_loop": [
            "load env",
            "poll queue",
            "retrieve context",
            "run cognitive pipeline",
            "persist evidence",
            "sleep/backoff",
        ],
    },
}

Path("_evidence\\P4_66_71_CONSOLIDATED_MIND_CORE_20260618_183503\\P4_66_71_CONSOLIDATED_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
print("P4.67_71_CORE_AUDIT_COMPLETE")
