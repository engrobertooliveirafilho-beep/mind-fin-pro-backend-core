import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

INPUT = Path("runtime/review_queue/runtime_review_queue.json")
OUTPUT = Path("runtime/prioritization/runtime_prioritized_queue.json")
EVIDENCE_DIR = Path("_evidence/P4.82_AUTO_PRIORITIZATION")

WEIGHTS = {
    "impact": 0.30,
    "risk": 0.20,
    "dependencies": 0.15,
    "complexity": 0.15,
    "expected_value": 0.20,
}

RISK_INVERSION = True

KEYWORDS = {
    "impact": {
        "runtime": 9, "retrieval": 9, "memory": 9, "governance": 8,
        "capability": 8, "drive": 8, "knowledge": 8, "graph": 7,
        "bug": 7, "test": 6, "adapter": 6, "orphan": 6
    },
    "risk": {
        "execution": 9, "lock": 9, "approval": 8, "gate": 8,
        "governance": 7, "runtime": 7, "merge": 6, "code": 6,
        "automatic": 6, "reconstruction": 5
    },
    "dependencies": {
        "graph": 9, "dependency": 9, "registry": 8, "retrieval": 8,
        "drive": 7, "memory": 7, "adapter": 6, "orphan": 6
    },
    "complexity": {
        "sovereign": 10, "full": 9, "repository": 9, "graph": 8,
        "merge": 8, "reconstruction": 8, "engine": 7, "automatic": 7,
        "capability": 6
    },
    "expected_value": {
        "prioritization": 10, "governance": 10, "reconstruction": 9,
        "knowledge": 9, "graph": 9, "recovery": 8, "gap": 8,
        "repository": 8, "certification": 8
    }
}

def stable_id(item, idx):
    raw = json.dumps(item, sort_keys=True, ensure_ascii=False) + str(idx)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def text_of(item):
    if isinstance(item, dict):
        return json.dumps(item, ensure_ascii=False).lower()
    return str(item).lower()

def score_dimension(text, dimension, default):
    score = default
    for kw, val in KEYWORDS.get(dimension, {}).items():
        if kw in text:
            score = max(score, val)
    return max(1, min(10, int(score)))

def normalize_missions(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ["missions", "items", "queue", "review_queue", "runtime_review_queue"]:
            if isinstance(data.get(key), list):
                return data[key]
    raise ValueError("Formato inválido: esperado array ou objeto contendo lista de missões.")

def priority_band(score):
    if score >= 8.0:
        return "P0_CRITICAL"
    if score >= 6.5:
        return "P1_HIGH"
    if score >= 5.0:
        return "P2_MEDIUM"
    return "P3_LOW"

def prioritize():
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    missions = normalize_missions(data)

    prioritized = []
    for idx, item in enumerate(missions):
        text = text_of(item)

        impact = score_dimension(text, "impact", 5)
        risk = score_dimension(text, "risk", 5)
        dependencies = score_dimension(text, "dependencies", 4)
        complexity = score_dimension(text, "complexity", 5)
        expected_value = score_dimension(text, "expected_value", 5)

        risk_component = (11 - risk) if RISK_INVERSION else risk
        complexity_component = 11 - complexity

        final_score = round(
            impact * WEIGHTS["impact"] +
            risk_component * WEIGHTS["risk"] +
            dependencies * WEIGHTS["dependencies"] +
            complexity_component * WEIGHTS["complexity"] +
            expected_value * WEIGHTS["expected_value"],
            4
        )

        enriched = {
            "priority_id": stable_id(item, idx),
            "source_index": idx,
            "status": "PENDING_REVIEW",
            "approval_required": True,
            "auto_execution_allowed": False,
            "priority_score": final_score,
            "priority_band": priority_band(final_score),
            "scoring": {
                "impact": impact,
                "risk": risk,
                "dependencies": dependencies,
                "complexity": complexity,
                "expected_value": expected_value,
                "weights": WEIGHTS,
                "risk_inversion": RISK_INVERSION
            },
            "mission": item
        }
        prioritized.append(enriched)

    prioritized.sort(key=lambda x: (-x["priority_score"], x["source_index"]))

    result = {
        "milestone": "P4.82 COMPLETE",
        "engine": "AUTO_PRIORITIZATION",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": str(INPUT),
        "output": str(OUTPUT),
        "total_missions": len(prioritized),
        "execution_policy": {
            "automatic_implementation": "FORBIDDEN",
            "review_required": True,
            "approval_required": True,
            "next_gate": "P4.83_SAFE_CODE_GENERATION_GATE"
        },
        "queue": prioritized
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    latest = EVIDENCE_DIR / "latest_runtime_prioritization_summary.json"
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps({
        "milestone": "P4.82 COMPLETE",
        "total_missions": len(prioritized),
        "top_priority": prioritized[0] if prioritized else None,
        "output": str(OUTPUT)
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "status": "P4.82 COMPLETE",
        "total_missions": len(prioritized),
        "output": str(OUTPUT)
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    prioritize()
