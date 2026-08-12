import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(".")
OUT = Path("runtime/capacity_audit")
OUT.mkdir(parents=True, exist_ok=True)

IGNORE_DIRS = {
    ".git", "__pycache__", ".pytest_cache", "venv", ".venv",
    "node_modules"
}

ACTIVE_ROOTS = ["app", "runtime", "tools", "tests"]
ARCHIVE_ROOTS = ["_evidence", "_backup", "backups", "evidence", "_maintenance", "_institutional"]

def is_ignored(p: Path):
    return any(part in IGNORE_DIRS for part in p.parts)

def rel(p):
    return str(p.as_posix())

def scan_files(root_name):
    root = Path(root_name)
    if not root.exists():
        return []
    files = []
    for p in root.rglob("*"):
        if p.is_file() and not is_ignored(p):
            files.append({
                "path": rel(p),
                "suffix": p.suffix.lower(),
                "size": p.stat().st_size
            })
    return files

def read_json(path):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": str(e)}

active_files = []
archive_files = []

for r in ACTIVE_ROOTS:
    active_files.extend(scan_files(r))

for r in ARCHIVE_ROOTS:
    archive_files.extend(scan_files(r))

registry = read_json("app/runtime/universal_capability_registry.json")
review_queue = read_json("runtime/review_queue/runtime_review_queue.json")
priority_queue = read_json("runtime/prioritization/runtime_prioritized_queue.json")

active_py = [f for f in active_files if f["suffix"] == ".py"]
archive_py = [f for f in archive_files if f["suffix"] == ".py"]
json_files = [f for f in active_files + archive_files if f["suffix"] == ".json"]

signals = {
    "active_python_files": len(active_py),
    "archive_python_files": len(archive_py),
    "active_total_files": len(active_files),
    "archive_total_files": len(archive_files),
    "json_files": len(json_files),
    "has_registry": registry is not None,
    "has_review_queue": review_queue is not None,
    "has_priority_queue": priority_queue is not None,
}

active_keywords = {
    "retrieval": [],
    "memory": [],
    "whatsapp": [],
    "cognitive_pipeline": [],
    "capability": [],
    "knowledge": [],
    "drive": [],
    "observability": [],
    "governance": [],
    "orphan": [],
}

for f in active_files:
    path = f["path"].lower()
    for k in active_keywords:
        if k in path:
            active_keywords[k].append(f["path"])

archive_keywords = {k: [] for k in active_keywords}
for f in archive_files:
    path = f["path"].lower()
    for k in archive_keywords:
        if k in path:
            archive_keywords[k].append(f["path"])

absorbed = []
pending = []

for k in active_keywords:
    if active_keywords[k]:
        absorbed.append({
            "capability": k,
            "status": "ACTIVE_OR_ABSORBED",
            "active_files": active_keywords[k][:30],
            "active_count": len(active_keywords[k]),
            "archive_count": len(archive_keywords[k])
        })
    elif archive_keywords[k]:
        pending.append({
            "capability": k,
            "status": "PENDING_RECOVERY_FROM_ARCHIVE_OR_DRIVE",
            "active_count": 0,
            "archive_count": len(archive_keywords[k]),
            "archive_samples": archive_keywords[k][:30]
        })

# detectar gargalos a partir dos testes/falhas conhecidas
technical_gaps = [
    {
        "gap": "Runtime response fallback dominance",
        "severity": "CRITICAL",
        "evidence": "Falhas anteriores indicam respostas genéricas sobrescrevendo contratos conversacionais.",
        "recommended_next": "P4.82C mapear imports reais e funções ativas antes de patch."
    },
    {
        "gap": "Observability state not accumulating events",
        "severity": "HIGH",
        "evidence": "audit_report/event_bus_report retornaram 0 após publish/audit_event.",
        "recommended_next": "Localizar app/eldora/core/audit_ledger.py e app/eldora/core/event_bus.py ativos."
    },
    {
        "gap": "Knowledge extraction under-detecting items",
        "severity": "MEDIUM",
        "evidence": "P479 retornou 2 itens quando o contrato espera >=3.",
        "recommended_next": "Corrigir extractor real, não teste."
    },
    {
        "gap": "Capability evidence scattered",
        "severity": "HIGH",
        "evidence": "Muitos snapshots em _evidence/backups sem índice único absorvido vs pendente.",
        "recommended_next": "Gerar ledger consolidado e fila de recovery."
    }
]

report = {
    "mission": "P4.82B PROJECT STATE AUDIT AND CAPACITY MAP",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "status": "AUDIT_COMPLETE",
    "p482": "COMPLETE",
    "green_seal": "BROKEN_BEFORE_THIS_AUDIT",
    "signals": signals,
    "absorbed_vs_active": absorbed,
    "pending_recovery": pending,
    "technical_gaps": technical_gaps,
    "next_recommended_mission": "P4.82C ACTIVE_RUNTIME_IMPORT_TRACE_AND_SURGICAL_RECOVERY",
    "rules": {
        "no_parallel_architecture": True,
        "no_auto_implementation_without_gate": True,
        "powershell_only": True,
        "preserve_evidence": True
    }
}

(OUT / "project_state_audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
Path("runtime/capability_map/absorbed_vs_pending_map.json").write_text(json.dumps({
    "absorbed": absorbed,
    "pending": pending
}, indent=2, ensure_ascii=False), encoding="utf-8")

Path("runtime/technical_gaps/technical_gap_report.json").write_text(json.dumps({
    "mission": "P4.82B",
    "technical_gaps": technical_gaps
}, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.82B AUDIT COMPLETE",
    "active_files": signals["active_total_files"],
    "archive_files": signals["archive_total_files"],
    "absorbed_capabilities": len(absorbed),
    "pending_capabilities": len(pending),
    "technical_gaps": len(technical_gaps),
    "next": "P4.82C ACTIVE_RUNTIME_IMPORT_TRACE_AND_SURGICAL_RECOVERY"
}, indent=2, ensure_ascii=False))
