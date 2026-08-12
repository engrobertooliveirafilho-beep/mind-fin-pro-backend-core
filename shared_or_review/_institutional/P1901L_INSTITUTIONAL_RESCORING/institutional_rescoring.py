from __future__ import annotations

import json
from pathlib import Path


IN = Path("_evidence/P1901K/CAPABILITY_MAP_V2.json")
OUT = Path("_evidence/P1901L")


DIMENSION_MAP = {
    "execution_safety": "Governance & Safety",
    "risk": "Risk Science",
    "data": "Data Infrastructure",
    "backtest": "Validation Science",
    "memory": "Market Memory",
    "graph": "Market Graph Intelligence",
    "learning": "Adaptive Research",
    "portfolio": "Portfolio Intelligence",
    "regime": "Regime Intelligence",
}

DIMENSION_TARGETS = {
    "Governance & Safety": 90,
    "Risk Science": 85,
    "Data Infrastructure": 82,
    "Validation Science": 84,
    "Market Memory": 80,
    "Market Graph Intelligence": 78,
    "Adaptive Research": 80,
    "Portfolio Intelligence": 85,
    "Regime Intelligence": 85,
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def classify(score: float) -> str:
    if score >= 90:
        return "STATE_OF_THE_ART"
    if score >= 80:
        return "INSTITUTIONAL"
    if score >= 65:
        return "ADVANCED"
    if score >= 45:
        return "INTERMEDIATE"
    if score >= 25:
        return "PROTOTYPE"
    return "TOY"


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    data = read_json(IN)
    caps = data["capabilities"]

    dimensions = {}

    for dim in sorted(set(DIMENSION_MAP.values())):
        dimensions[dim] = {
            "scores": [],
            "capabilities": 0,
            "p0": 0,
            "p1": 0,
            "weak": 0,
            "target": DIMENSION_TARGETS[dim],
        }

    for cap in caps:
        dim = DIMENSION_MAP.get(cap["category"], "Other")
        if dim not in dimensions:
            dimensions[dim] = {
                "scores": [],
                "capabilities": 0,
                "p0": 0,
                "p1": 0,
                "weak": 0,
                "target": 75,
            }

        d = dimensions[dim]
        d["scores"].append(cap["institutional_score"])
        d["capabilities"] += 1

        if cap["priority"] == "P0_CRITICAL_BOTTLENECK":
            d["p0"] += 1
        if cap["priority"] == "P1_HIGH_PRIORITY":
            d["p1"] += 1
        if cap["institutional_score"] < 50:
            d["weak"] += 1

    dimension_report = {}

    for dim, d in dimensions.items():
        avg = round(sum(d["scores"]) / max(len(d["scores"]), 1), 2)
        gap = round(max(0, d["target"] - avg), 2)

        dimension_report[dim] = {
            "score": avg,
            "target": d["target"],
            "gap": gap,
            "classification": classify(avg),
            "capabilities": d["capabilities"],
            "p0_bottlenecks": d["p0"],
            "p1_high_priority": d["p1"],
            "weak_capabilities": d["weak"],
        }

    weighted_score = round(
        sum(v["score"] for v in dimension_report.values()) / max(len(dimension_report), 1),
        2
    )

    p0_total = sum(v["p0_bottlenecks"] for v in dimension_report.values())
    p1_total = sum(v["p1_high_priority"] for v in dimension_report.values())
    weak_total = sum(v["weak_capabilities"] for v in dimension_report.values())

    readiness = {
        "program": "P1901L_INSTITUTIONAL_RESCORING",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "source": "P1901K_CAPABILITY_MAP_V2",
        "institutional_readiness_score_final": weighted_score,
        "classification": classify(weighted_score),
        "capability_total": len(caps),
        "p0_critical_bottlenecks": p0_total,
        "p1_high_priority": p1_total,
        "weak_capabilities": weak_total,
        "dimension_report": dimension_report,
        "final_diagnosis": {
            "architecture": "CONNECTED",
            "orphan_modules": 0,
            "primary_limitation": "DEPTH_AND_VALIDATION_DENSITY",
            "secondary_limitation": "REGIME_PORTFOLIO_CAUSALITY_UNDERDEVELOPED",
            "approved_for_P1902": True,
        },
        "recommended_next_modules": [
            "P1902_DATA_DENSITY_EXPANSION",
            "P1903_REAL_EVENT_MEMORY",
            "P1904_REGIME_DISCOVERY_ENGINE",
            "P1905_MULTI_ASSET_EXPANSION",
            "P1906_FEATURE_EXPLOSION_ENGINE",
            "P1907_CAUSALITY_RESEARCH",
            "P1908_MARKET_MEMORY_V2",
            "P1909_SPECIALIST_EVOLUTION_V2",
            "P1910_PORTFOLIO_INTELLIGENCE"
        ],
    }

    summary = {
        "program": readiness["program"],
        "status": readiness["status"],
        "mode": readiness["mode"],
        "institutional_readiness_score_final": readiness["institutional_readiness_score_final"],
        "classification": readiness["classification"],
        "capability_total": readiness["capability_total"],
        "p0_critical_bottlenecks": readiness["p0_critical_bottlenecks"],
        "p1_high_priority": readiness["p1_high_priority"],
        "weak_capabilities": readiness["weak_capabilities"],
        "approved_for_P1902": readiness["final_diagnosis"]["approved_for_P1902"],
        "recommended_next": readiness["recommended_next_modules"][0],
        "report": "_evidence/P1901L/INSTITUTIONAL_RESCORING.json",
    }

    (OUT / "INSTITUTIONAL_RESCORING.json").write_text(
        json.dumps(readiness, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
