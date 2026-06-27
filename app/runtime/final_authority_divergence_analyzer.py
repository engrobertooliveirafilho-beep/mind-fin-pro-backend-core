import json
from pathlib import Path
from collections import Counter


def analyze_canary_diff(path: str):
    p = Path(path)
    records = []

    if not p.exists():
        return {
            "ok": False,
            "reason": "CANARY_LOG_NOT_FOUND",
            "path": str(p),
            "total": 0,
            "promotion_ready": False,
        }

    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except Exception:
            records.append({"parse_error": True, "raw": line[:500]})

    total = len(records)
    if total == 0:
        return {
            "ok": False,
            "reason": "CANARY_LOG_EMPTY",
            "path": str(p),
            "total": 0,
            "promotion_ready": False,
        }

    selected_matches_legacy = sum(1 for r in records if r.get("selected_matches_legacy") is True)
    selected_matches_candidate = sum(1 for r in records if r.get("selected_matches_candidate") is True)
    candidate_matches_legacy = sum(1 for r in records if r.get("candidate_matches_legacy") is True)
    errors = sum(1 for r in records if r.get("error") or r.get("parse_error"))

    sources = Counter(str(r.get("source", "unknown")) for r in records)

    divergences = []
    for r in records:
        critical = False
        reason = []

        if r.get("error") or r.get("parse_error"):
            critical = True
            reason.append("error_or_parse_error")

        if r.get("selected_matches_legacy") is False:
            reason.append("selected_differs_from_legacy")

        if r.get("selected_matches_candidate") is False:
            reason.append("selected_differs_from_candidate")

        severity = "INFO"
        if reason:
            severity = "ACCEPTABLE"
        if critical:
            severity = "CRITICAL"

        divergences.append({
            "severity": severity,
            "source": r.get("source"),
            "legacy_hash": r.get("legacy_hash"),
            "candidate_hash": r.get("candidate_hash"),
            "selected_hash": r.get("selected_hash"),
            "reason": reason,
        })

    severity_count = Counter(d["severity"] for d in divergences)

    equivalence_rate = selected_matches_legacy / total if total else 0.0
    error_rate = errors / total if total else 0.0

    promotion_ready = (
        total >= 10
        and equivalence_rate >= 0.98
        and error_rate == 0
        and severity_count.get("CRITICAL", 0) == 0
    )

    return {
        "ok": True,
        "path": str(p),
        "total": total,
        "selected_matches_legacy": selected_matches_legacy,
        "selected_matches_candidate": selected_matches_candidate,
        "candidate_matches_legacy": candidate_matches_legacy,
        "equivalence_rate": equivalence_rate,
        "error_rate": error_rate,
        "sources": dict(sources),
        "severity_count": dict(severity_count),
        "promotion_ready": promotion_ready,
        "promotion_gate": {
            "min_samples": 10,
            "required_equivalence_rate": 0.98,
            "required_error_rate": 0.0,
            "critical_divergences_allowed": 0,
        },
        "divergences": divergences[-100:],
    }
