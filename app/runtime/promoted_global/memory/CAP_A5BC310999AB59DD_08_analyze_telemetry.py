import json
from pathlib import Path
from collections import Counter, defaultdict

telemetry = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")
out = {
    "exists": telemetry.exists(),
    "total_lines": 0,
    "by_domain": {},
    "by_sender": {},
    "recovered_counts": {},
    "nonzero_samples": [],
    "zero_samples": [],
}

if telemetry.exists():
    lines = telemetry.read_text(encoding="utf-8", errors="ignore").splitlines()
    out["total_lines"] = len(lines)

    by_domain = Counter()
    by_sender = Counter()
    recovered_counts = Counter()

    for line in lines:
        try:
            obj = json.loads(line)
        except Exception:
            continue

        by_domain[obj.get("active_domain") or "unknown"] += 1
        by_sender[obj.get("sender") or "unknown"] += 1
        recovered_counts[str(obj.get("recovered_shadow_context_count", 0))] += 1

        if obj.get("recovered_shadow_context_count", 0):
            out["nonzero_samples"].append(obj)
        else:
            if len(out["zero_samples"]) < 10:
                out["zero_samples"].append(obj)

    out["by_domain"] = dict(by_domain)
    out["by_sender"] = dict(by_sender)
    out["recovered_counts"] = dict(recovered_counts)

Path("_evidence/P19P36I_SHADOW_TELEMETRY_ANALYSIS_20260621_230232/telemetry_analysis.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2))
