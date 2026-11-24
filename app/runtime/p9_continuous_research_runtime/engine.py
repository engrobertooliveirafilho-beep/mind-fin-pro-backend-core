import json, time
from pathlib import Path
from ..p9_edge_discovery_factory.engine import run as run_edge_factory

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
    if not isinstance(cycle_id,str) or not cycle_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for c in cycle_id) or cycle_id in (".",".."):
        raise ValueError("invalid cycle identifier")
    out=Path("reports/P9.6_CONTINUOUS_RESEARCH_RUNTIME")
    out.mkdir(parents=True,exist_ok=True)
    edge_manifest=run_edge_factory()
    cycle={
        "cycle_id":cycle_id,
        "status":"PARTIAL_SYNTHETIC_RESEARCH_ONLY",
        "step_status":{step: ("SYNTHETIC_RESEARCH" if step in ("genome_generation","massive_backtest_grid") else "REPORT_WRITTEN_ON_RETURN" if step=="reports" else "BLOCKED_UNVERIFIED" if step=="paper_candidate_ranking" else "NOT_EXECUTED") for step in STEPS},
        "validation_executed":False,
        "e2e_certified":False,
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
