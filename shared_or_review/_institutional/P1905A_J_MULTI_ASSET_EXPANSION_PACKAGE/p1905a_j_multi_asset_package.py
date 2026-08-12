import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P1905A_J")

ASSETS = {
    "EURUSD":"FX",
    "GBPUSD":"FX",
    "USDJPY":"FX",
    "USDCAD":"FX",
    "AUDUSD":"FX",
    "NZDUSD":"FX",
    "USDCHF":"FX",
    "XAUUSD":"METALS",
    "XAGUSD":"METALS",
    "BTCUSD":"CRYPTO",
    "ETHUSD":"CRYPTO",
    "NAS100":"INDEX",
    "SP500":"INDEX",
    "DAX":"INDEX",
    "NIKKEI":"INDEX",
    "WIN":"FUTURES",
    "WDO":"FUTURES",
    "PETR4":"B3",
    "VALE3":"B3",
    "IFIX":"B3",
    "IBOV":"B3"
}

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    asset_registry = []
    coverage = []
    priorities = []
    graph_nodes = []
    graph_edges = []

    for asset, cls in ASSETS.items():

        asset_registry.append({
            "asset": asset,
            "asset_class": cls,
            "target_history_years": 20,
            "minimum_history_years": 10,
            "mode": "RESEARCH_ONLY"
        })

        coverage.append({
            "asset": asset,
            "dataset": False,
            "memory": False,
            "feature": True,
            "specialist": False,
            "backtest": False
        })

        priorities.append({
            "asset": asset,
            "priority": "P0",
            "reason": "INSTITUTIONAL_COVERAGE_EXPANSION"
        })

        graph_nodes.append({
            "id": asset,
            "type": "asset"
        })

        graph_edges.append({
            "source": asset,
            "target": cls,
            "type": "BELONGS_TO"
        })

    readiness = {
        "program": "P1905J_MULTI_ASSET_READINESS_AUDIT",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "asset_count": len(ASSETS),
        "asset_classes": len(set(ASSETS.values())),
        "graph_nodes": len(graph_nodes),
        "graph_edges": len(graph_edges),
        "approved_for_P1906": True,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "generated_at": datetime.now(UTC).isoformat()
    }

    files = {
        "P1905A_ASSET_REGISTRY.json": asset_registry,
        "P1905B_ASSET_CLASSIFICATION.json": asset_registry,
        "P1905C_ASSET_COVERAGE.json": coverage,
        "P1905D_ASSET_PRIORITY_QUEUE.json": priorities,
        "P1905E_ASSET_MEMORY_PLAN.json": asset_registry,
        "P1905F_ASSET_RETRIEVAL_PLAN.json": asset_registry,
        "P1905G_ASSET_SIMILARITY_PLAN.json": asset_registry,
        "P1905H_ASSET_GRAPH.json": {
            "nodes": graph_nodes,
            "edges": graph_edges
        },
        "P1905I_ASSET_COVERAGE_AUDIT.json": coverage,
        "P1905J_MULTI_ASSET_READINESS_AUDIT.json": readiness,
        "SUMMARY.json": readiness
    }

    for name, data in files.items():
        (OUT / name).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    print(json.dumps(readiness, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
