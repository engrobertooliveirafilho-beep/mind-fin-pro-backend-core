import json, time
from pathlib import Path
from app.p9_edge_discovery_factory.engine import run as run_edge_factory

STEPS=[
    "new_data_scan",
    "dataset_catalog",
    "dataset_quality_gate",
    "genome_generation",
    "massive_backtest_grid",
    "walk_forward",
    "monte_carlo",
    "robustness_committee",
    "paper_candidate_ranking",
    "reports"
]

def run_cycle(cycle_id="P9.6_CYCLE_001"):
    out=Path("reports/P9.6_CONTINUOUS_RESEARCH_RUNTIME")
    out.mkdir(parents=True,exist_ok=True)
    edge_manifest=run_edge_factory()
    cycle={
        "cycle_id":cycle_id,
        "status":"COMPLETED_RESEARCH_ONLY",
        "steps":STEPS,
        "edge_factory_status":edge_manifest["STATUS"],
        "live":"FORBIDDEN",
        "production":"BLOCKED",
        "real_broker":"DISABLED",
        "ftmo_real":"FORBIDDEN",
        "promotion_allowed":False,
        "edge":"NOT_PROVEN",
        "causality":"NOT_PROVEN",
        "export_ready":True
    }
    (out/f"{cycle_id}.json").write_text(json.dumps(cycle,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P9.6_manifest.json").write_text(json.dumps(cycle,indent=2,ensure_ascii=False),encoding="utf-8")
    return cycle

if __name__=="__main__":
    print(json.dumps(run_cycle(),indent=2,ensure_ascii=False))
