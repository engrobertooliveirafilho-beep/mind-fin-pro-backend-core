import json
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

ROOT = Path.cwd()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT = ROOT / "_evidence" / f"P4.45M_MASTER_MATRIX_RECONCILIATION_{TS}"
REPORTS = OUT / "reports"
MATRICES = OUT / "matrices"

REPORTS.mkdir(parents=True, exist_ok=True)
MATRICES.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "MIND_CAPABILITY_STATUS_MATRIX.json",
    "MIND_GAP_MATRIX.json",
    "MIND_UNCONNECTED_CAPABILITY_LEDGER.json",
    "MIND_DEAD_CAPABILITY_LEDGER.json",
    "MIND_RUNTIME_CONNECTIVITY_MATRIX.json",
    "RUNTIME_COVERAGE_MATRIX.json",
    "P5_13_CAPABILITY_DECISION_MATRIX.json",
    "DRIVE_SCAN_CAPABILITY_SUMMARY.json",
    "DRIVE_SCAN_IMPORTANT_CANDIDATES.json",
    "DRIVE_SCAN_MATCHED_CAPABILITIES.json",
]

def latest_file(name):
    files = list(ROOT.rglob(name))
    files = [f for f in files if "_evidence" in str(f) or f.parent == ROOT]
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_load_error": str(e), "_path": str(path)}

sources = {}
for name in TARGETS:
    f = latest_file(name)
    if f:
        sources[name] = {
            "path": str(f),
            "size": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat(),
            "data": load_json(f)
        }
    else:
        sources[name] = {
            "path": None,
            "size": 0,
            "modified": None,
            "data": None
        }

capabilities = defaultdict(lambda: {
    "capability": "",
    "exists": "UNKNOWN",
    "connectivity": "UNKNOWN",
    "maturity": "UNKNOWN",
    "review_status": "UNKNOWN",
    "symbol_count": 0,
    "file_count": 0,
    "active_evidence_count": 0,
    "drive_hits_total": 0,
    "drive_hits_clean": 0,
    "candidate_count_positive": 0,
    "priority": "UNSET",
    "decision": "UNSET",
    "sources": [],
    "risk": "UNKNOWN",
    "recommended_action": "REVIEW"
})

def upsert_capability(name, source_name, item):
    if not name:
        return

    c = capabilities[name]
    c["capability"] = name
    c["sources"].append(source_name)

    for k in ["exists", "connectivity", "maturity", "review_status", "priority", "decision"]:
        if isinstance(item, dict) and item.get(k):
            c[k] = item.get(k)

    for k in ["symbol_count", "file_count", "active_evidence_count", "drive_hits_total", "drive_hits_clean", "candidate_count_positive"]:
        if isinstance(item, dict) and isinstance(item.get(k), int):
            c[k] = max(c[k], item.get(k))

# Capability status / gaps / ledgers
for source_name in [
    "MIND_CAPABILITY_STATUS_MATRIX.json",
    "MIND_GAP_MATRIX.json",
    "MIND_UNCONNECTED_CAPABILITY_LEDGER.json",
    "MIND_DEAD_CAPABILITY_LEDGER.json",
    "DRIVE_SCAN_CAPABILITY_SUMMARY.json",
    "P5_13_CAPABILITY_DECISION_MATRIX.json",
]:
    data = sources[source_name]["data"]
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                upsert_capability(item.get("capability"), source_name, item)

# Runtime connectivity: files -> capabilities
runtime_data = sources["MIND_RUNTIME_CONNECTIVITY_MATRIX.json"]["data"]
if isinstance(runtime_data, list):
    for item in runtime_data:
        if isinstance(item, dict):
            for cap in item.get("capabilities", []) or []:
                upsert_capability(cap, "MIND_RUNTIME_CONNECTIVITY_MATRIX.json", {
                    "file_count": 1,
                    "connectivity": "RUNTIME_FILE_FOUND"
                })

# Drive matched capabilities
for source_name in ["DRIVE_SCAN_IMPORTANT_CANDIDATES.json", "DRIVE_SCAN_MATCHED_CAPABILITIES.json"]:
    data = sources[source_name]["data"]
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for cap in item.get("capabilities", []) or []:
                    upsert_capability(cap, source_name, {
                        "drive_hits_total": 1,
                        "drive_hits_clean": 0 if item.get("is_noise") else 1
                    })

master = []

for cap, row in capabilities.items():
    row["sources"] = sorted(set(row["sources"]))

    if row["connectivity"] in ["ATIVA", "RUNTIME_FILE_FOUND"] and row["active_evidence_count"] > 0:
        row["risk"] = "LOW"
        row["recommended_action"] = "CERTIFY_OR_KEEP"
    elif row["exists"] == "PARCIAL" or "DESCONECTADA" in row["connectivity"]:
        row["risk"] = "HIGH"
        row["recommended_action"] = "RECONCILE_AND_WIRE"
    elif row["drive_hits_clean"] > 0 and row["active_evidence_count"] == 0:
        row["risk"] = "MEDIUM"
        row["recommended_action"] = "READ_CODE_AND_DECIDE"
    else:
        row["risk"] = "MEDIUM"
        row["recommended_action"] = "MANUAL_REVIEW"

    master.append(row)

master = sorted(master, key=lambda x: (
    {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "UNKNOWN": 3}.get(x["risk"], 9),
    -x["candidate_count_positive"],
    -x["drive_hits_clean"],
    x["capability"]
))

summary = {
    "program": "P4.45M_MASTER_MATRIX_RECONCILIATION",
    "status": "PASS",
    "mode": "EVIDENCE_ONLY_NO_RUNTIME_WRITE",
    "runtime_modified": False,
    "production_enabled": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "sources_loaded": [
        {
            "name": k,
            "path": v["path"],
            "size": v["size"],
            "modified": v["modified"],
            "loaded": v["data"] is not None and not (isinstance(v["data"], dict) and "_load_error" in v["data"])
        }
        for k, v in sources.items()
    ],
    "capabilities_total": len(master),
    "risk_high": sum(1 for x in master if x["risk"] == "HIGH"),
    "risk_medium": sum(1 for x in master if x["risk"] == "MEDIUM"),
    "risk_low": sum(1 for x in master if x["risk"] == "LOW"),
    "top_critical": master[:20],
}

(MATRICES / "MASTER_CAPABILITY_MATRIX.json").write_text(json.dumps(master, indent=2, ensure_ascii=False), encoding="utf-8")
(REPORTS / "MASTER_EXECUTIVE_SNAPSHOT.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

txt = []
txt.append("P4.45M MASTER MATRIX RECONCILIATION")
txt.append(f"STATUS: {summary['status']}")
txt.append(f"MODE: {summary['mode']}")
txt.append(f"CAPABILITIES_TOTAL: {summary['capabilities_total']}")
txt.append(f"RISK_HIGH: {summary['risk_high']}")
txt.append(f"RISK_MEDIUM: {summary['risk_medium']}")
txt.append(f"RISK_LOW: {summary['risk_low']}")
txt.append("")
txt.append("TOP 20 CRITICAL:")
for x in master[:20]:
    txt.append(f"- {x['capability']} | risk={x['risk']} | exists={x['exists']} | connectivity={x['connectivity']} | action={x['recommended_action']}")

(REPORTS / "MASTER_EXECUTIVE_SNAPSHOT.txt").write_text("\n".join(txt), encoding="utf-8")

print(json.dumps(summary, indent=2, ensure_ascii=False))
