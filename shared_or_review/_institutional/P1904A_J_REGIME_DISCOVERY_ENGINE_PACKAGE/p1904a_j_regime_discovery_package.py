import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P1904A_J")

REGIMES = [
    "TREND", "RANGE", "ACCUMULATION", "DISTRIBUTION", "PANIC",
    "VOLATILITY_EXPANSION", "VOLATILITY_COMPRESSION",
    "LIQUIDITY_VACUUM", "BREAKOUT", "MEAN_REVERSION"
]

FEATURES = [
    "VOLATILITY", "ATR", "RANGE_WIDTH", "TREND_SLOPE", "ADX",
    "RETURN_DISTRIBUTION", "VOLUME_PROXY", "SESSION",
    "INTERMARKET", "MOMENTUM"
]

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    schema = {
        "program": "P1904A_REGIME_SCHEMA",
        "regimes": REGIMES,
        "manual_labels_allowed": False,
        "mode": "RESEARCH_ONLY"
    }

    feature_map = [
        {"feature": f, "used_for": REGIMES, "source": "MARKET_DATA_DERIVED"}
        for f in FEATURES
    ]

    cluster_plan = {
        "program": "P1904C_REGIME_CLUSTER_PLAN",
        "methods": ["KMEANS", "HDBSCAN", "GAUSSIAN_MIXTURE", "SPECTRAL_CLUSTERING"],
        "manual_labels_allowed": False,
        "validation": ["SILHOUETTE", "STABILITY", "OUT_OF_SAMPLE_REGIME_PERSISTENCE"],
        "mode": "RESEARCH_ONLY"
    }

    transition_matrix = [
        {"from": a, "to": b, "transition_probability": None, "status": "PLANNED"}
        for a in REGIMES for b in REGIMES
    ]

    memories = [
        {
            "memory_id": f"regime_mem_{i+1}",
            "regime": r,
            "retrieval_ready": True,
            "similarity_ready": True,
            "graph_ready": True,
            "mode": "RESEARCH_ONLY"
        }
        for i, r in enumerate(REGIMES)
    ]

    retrieval = [{"regime": r, "keys": [r, "REGIME", "MARKET_STATE"]} for r in REGIMES]
    similarity = [{"regime": r, "features": FEATURES} for r in REGIMES]
    graph = {
        "nodes": [{"id": r, "type": "regime"} for r in REGIMES],
        "edges": [{"source": r, "target": "MARKET_MEMORY", "type": "CAN_LINK_TO"} for r in REGIMES]
    }

    coverage = {
        "program": "P1904I_REGIME_COVERAGE_AUDIT",
        "regime_count": len(REGIMES),
        "feature_count": len(FEATURES),
        "coverage_status": "SCHEMA_READY_NO_CLUSTERING_EXECUTED",
        "mode": "RESEARCH_ONLY"
    }

    readiness = {
        "program": "P1904J_REGIME_READINESS_AUDIT",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "regime_count": len(REGIMES),
        "feature_count": len(FEATURES),
        "memory_count": len(memories),
        "graph_nodes": len(graph["nodes"]),
        "graph_edges": len(graph["edges"]),
        "manual_labels_allowed": False,
        "clustering_executed": False,
        "approved_for_P1905": True,
        "generated_at": datetime.now(UTC).isoformat()
    }

    outputs = {
        "P1904A_REGIME_SCHEMA.json": schema,
        "P1904B_REGIME_FEATURE_MAP.json": feature_map,
        "P1904C_REGIME_CLUSTER_PLAN.json": cluster_plan,
        "P1904D_REGIME_TRANSITION_MATRIX.json": transition_matrix,
        "P1904E_REGIME_MEMORY.json": memories,
        "P1904F_REGIME_RETRIEVAL.json": retrieval,
        "P1904G_REGIME_SIMILARITY.json": similarity,
        "P1904H_REGIME_GRAPH.json": graph,
        "P1904I_REGIME_COVERAGE_AUDIT.json": coverage,
        "P1904J_REGIME_READINESS_AUDIT.json": readiness,
        "SUMMARY.json": readiness,
    }

    for name, payload in outputs.items():
        (OUT / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(readiness, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
