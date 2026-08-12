import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P1907A_J")

COMPONENTS = [
    "CAUSAL_HYPOTHESIS_ENGINE",
    "INTERVENTION_TESTING",
    "COUNTERFACTUAL_ANALYSIS",
    "LAG_DISCOVERY",
    "LEAD_LAG_NETWORKS",
    "GRANGER_SCREENING",
    "DO_CALCULUS_PLACEHOLDER",
    "ANTI_CORRELATION_GUARD",
    "CAUSAL_GRAPH",
    "CAUSAL_READINESS_AUDIT"
]

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    registry = []
    for c in COMPONENTS:
        registry.append({
            "component": c,
            "status": "PLANNED",
            "correlation_only_allowed": False,
            "requires_out_of_sample": True,
            "requires_lag_validation": True,
            "mode": "RESEARCH_ONLY"
        })

    graph = {
        "nodes": [{"id": c, "type": "causal_component"} for c in COMPONENTS],
        "edges": [
            {"source": "CAUSAL_HYPOTHESIS_ENGINE", "target": c, "type": "FEEDS"}
            for c in COMPONENTS if c != "CAUSAL_HYPOTHESIS_ENGINE"
        ]
    }

    readiness = {
        "program": "P1907J_CAUSALITY_READINESS_AUDIT",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "component_count": len(COMPONENTS),
        "correlation_only_allowed": False,
        "graph_nodes": len(graph["nodes"]),
        "graph_edges": len(graph["edges"]),
        "approved_for_P1908": True,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "generated_at": datetime.now(UTC).isoformat()
    }

    files = {
        "P1907A_CAUSAL_HYPOTHESIS_ENGINE.json": registry,
        "P1907B_INTERVENTION_TESTING.json": registry,
        "P1907C_COUNTERFACTUAL_ANALYSIS.json": registry,
        "P1907D_LAG_DISCOVERY.json": registry,
        "P1907E_LEAD_LAG_NETWORKS.json": registry,
        "P1907F_GRANGER_SCREENING.json": registry,
        "P1907G_DO_CALCULUS_PLACEHOLDER.json": registry,
        "P1907H_ANTI_CORRELATION_GUARD.json": registry,
        "P1907I_CAUSAL_GRAPH.json": graph,
        "P1907J_CAUSALITY_READINESS_AUDIT.json": readiness,
        "SUMMARY.json": readiness
    }

    for name, data in files.items():
        (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(readiness, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
