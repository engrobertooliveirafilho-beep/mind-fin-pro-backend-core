from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict


IN = Path("_evidence/P1901J/RUNTIME_GRAPH_V2.json")
OUT = Path("_evidence/P1901K")


CATEGORY_TARGETS = {
    "execution_safety": 85,
    "risk": 80,
    "data": 78,
    "backtest": 78,
    "memory": 75,
    "graph": 75,
    "learning": 75,
    "portfolio": 80,
    "regime": 82,
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_priority(node: dict) -> str:
    cat = node["category"]
    score = node["institutional_score"]
    degree = node["total_degree"]
    critical = node["criticality"] == "CRITICAL"

    target = CATEGORY_TARGETS.get(cat, 75)
    gap = target - score

    if critical and gap >= 40 and degree >= 5:
        return "P0_CRITICAL_BOTTLENECK"
    if critical and gap >= 25:
        return "P1_HIGH_PRIORITY"
    if gap >= 20:
        return "P2_MEDIUM_PRIORITY"
    if gap > 0:
        return "P3_LOW_PRIORITY"
    return "P4_STABLE"


def expansion_recommendation(node: dict) -> list[str]:
    cat = node["category"]
    score = node["institutional_score"]
    recs = []

    if score < 50:
        recs.append("INCREASE_CODE_AND_LOGIC_DENSITY")

    if cat == "data":
        recs += ["ADD_DATA_QUALITY_GATES", "ADD_COVERAGE_AUDIT", "ADD_NORMALIZATION_VALIDATION"]
    elif cat == "backtest":
        recs += ["ADD_WALK_FORWARD", "ADD_MONTE_CARLO", "ADD_PURGED_VALIDATION", "ADD_SLIPPAGE_MODEL"]
    elif cat == "memory":
        recs += ["ADD_RETRIEVAL_INDEX", "ADD_SIMILARITY_SEARCH", "ADD_CONTEXT_VERSIONING", "ADD_MEMORY_DECAY"]
    elif cat == "graph":
        recs += ["ADD_NODE_EDGE_SCHEMA", "ADD_GRAPH_METRICS", "ADD_COMMUNITY_DETECTION"]
    elif cat == "learning":
        recs += ["ADD_OUT_OF_SAMPLE_SELECTION", "ADD_EXTINCTION_RULES", "ADD_DECAY_MONITORING"]
    elif cat == "portfolio":
        recs += ["ADD_EXPOSURE_ENGINE", "ADD_CORRELATION_MATRIX", "ADD_RISK_BUDGETING", "ADD_DRAWDOWN_CONTROL"]
    elif cat == "regime":
        recs += ["ADD_UNSUPERVISED_CLUSTERING", "ADD_VOLATILITY_STATE_MODEL", "ADD_REGIME_TRANSITION_MATRIX"]
    elif cat == "risk":
        recs += ["ADD_LEAKAGE_SCANNER", "ADD_LOOKAHEAD_TESTS", "ADD_SURVIVORSHIP_AUDIT"]
    elif cat == "execution_safety":
        recs += ["ADD_HARD_RUNTIME_LOCK", "ADD_ORDER_ROUTER_NULL_OBJECT", "ADD_BROKER_KILL_SWITCH"]

    return sorted(set(recs))


def build_capability_map_v2():
    OUT.mkdir(parents=True, exist_ok=True)

    graph = read_json(IN)
    nodes = graph["nodes"]

    mapped = []
    by_category = defaultdict(list)
    by_priority = defaultdict(list)

    for node in nodes:
        priority = classify_priority(node)
        target = CATEGORY_TARGETS.get(node["category"], 75)
        gap = max(0, target - node["institutional_score"])

        row = {
            "capability_id": node["id"],
            "file": node["file"],
            "owner_module": node["owner_module"],
            "category": node["category"],
            "type": node["type"],
            "maturity": node["maturity"],
            "institutional_score": node["institutional_score"],
            "target_score": target,
            "gap_to_target": gap,
            "total_degree": node["total_degree"],
            "criticality": node["criticality"],
            "priority": priority,
            "expansion_recommendations": expansion_recommendation(node),
        }

        mapped.append(row)
        by_category[row["category"]].append(row)
        by_priority[row["priority"]].append(row)

    category_summary = {}

    for cat, items in by_category.items():
        avg_score = round(sum(i["institutional_score"] for i in items) / len(items), 2)
        avg_gap = round(sum(i["gap_to_target"] for i in items) / len(items), 2)

        category_summary[cat] = {
            "count": len(items),
            "avg_score": avg_score,
            "avg_gap": avg_gap,
            "target": CATEGORY_TARGETS.get(cat, 75),
            "p0": sum(1 for i in items if i["priority"] == "P0_CRITICAL_BOTTLENECK"),
            "p1": sum(1 for i in items if i["priority"] == "P1_HIGH_PRIORITY"),
            "weak": sum(1 for i in items if i["institutional_score"] < 50),
        }

    upgrade_queue = sorted(
        mapped,
        key=lambda x: (
            {"P0_CRITICAL_BOTTLENECK": 0, "P1_HIGH_PRIORITY": 1, "P2_MEDIUM_PRIORITY": 2, "P3_LOW_PRIORITY": 3, "P4_STABLE": 4}[x["priority"]],
            -x["gap_to_target"],
            -x["total_degree"],
            x["category"],
        )
    )

    result = {
        "program": "P1901K_CAPABILITY_MAP_V2",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "source": "P1901J_RUNTIME_GRAPH_V2",
        "capability_total": len(mapped),
        "category_summary": dict(sorted(category_summary.items())),
        "priority_summary": {k: len(v) for k, v in sorted(by_priority.items())},
        "institutional_readiness_score_v2": round(
            sum(i["institutional_score"] for i in mapped) / max(len(mapped), 1),
            2
        ),
        "avg_gap_to_institutional_target": round(
            sum(i["gap_to_target"] for i in mapped) / max(len(mapped), 1),
            2
        ),
        "top_50_upgrade_queue": upgrade_queue[:50],
        "approved_for_P1901L": len(upgrade_queue) > 0,
        "capabilities": mapped,
    }

    summary = {
        "program": result["program"],
        "status": result["status"],
        "mode": result["mode"],
        "capability_total": result["capability_total"],
        "institutional_readiness_score_v2": result["institutional_readiness_score_v2"],
        "avg_gap_to_institutional_target": result["avg_gap_to_institutional_target"],
        "priority_summary": result["priority_summary"],
        "category_summary": result["category_summary"],
        "approved_for_P1901L": result["approved_for_P1901L"],
        "report": "_evidence/P1901K/CAPABILITY_MAP_V2.json",
    }

    (OUT / "CAPABILITY_MAP_V2.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return summary


if __name__ == "__main__":
    print(json.dumps(build_capability_map_v2(), indent=2, ensure_ascii=False))
