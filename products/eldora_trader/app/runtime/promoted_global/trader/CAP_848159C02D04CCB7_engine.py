import json
from pathlib import Path
from app.p9_continuous_research_runtime.engine import run_cycle

DASHBOARDS=[
    "top_genomes",
    "top_dna",
    "top_datasets",
    "top_regimes",
    "top_robustness",
    "top_paper_candidates",
    "top_correlations",
    "uncertainty_alerts"
]

def safe_load(path, default):
    p=Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

def build_dashboard():
    out=Path("reports/P9.7_RESEARCH_COMMAND_CENTER")
    out.mkdir(parents=True,exist_ok=True)
    run_cycle("P9.7_COMMAND_CENTER_BUILD")
    rankings=safe_load("reports/P9.3_MASSIVE_BACKTEST_GRID/P9.3_top_ranked_candidates.json",[])
    paper=safe_load("reports/P9.5_EDGE_DISCOVERY_FACTORY/P9.5_paper_candidates.json",[])
    catalog=safe_load("reports/P9.1_DATA_EXPANSION_ENGINE/dataset_catalog.json",[])
    dashboard={
        "status":"P9.7_RESEARCH_COMMAND_CENTER_IMPLEMENTED",
        "dashboards":DASHBOARDS,
        "top_genomes":rankings[:25],
        "top_paper_candidates":paper[:25],
        "top_datasets":catalog[:25],
        "top_dna":safe_load("reports/P9.4_DNA_EXTRACTION_ENGINE/P9.4_dna_candidates.json",{}),
        "top_regimes":{},
        "top_robustness":safe_load("reports/P9.5_EDGE_DISCOVERY_FACTORY/P9.5_candidate_evaluations.json",[])[:25],
        "top_correlations":[],
        "uncertainty_alerts":[
            "EDGE_NOT_PROVEN",
            "CAUSALITY_NOT_PROVEN",
            "REAL_DATA_CERTIFICATION_REQUIRED",
            "LIVE_FORBIDDEN",
            "PROMOTION_REAL_BLOCKED"
        ],
        "live":"FORBIDDEN",
        "production":"BLOCKED",
        "real_broker":"DISABLED",
        "ftmo_real":"FORBIDDEN",
        "promotion_allowed":False,
        "export_ready":True
    }
    (out/"P9.7_dashboard.json").write_text(json.dumps(dashboard,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P9.7_manifest.json").write_text(json.dumps({
        "STATUS":dashboard["status"],
        "DASHBOARDS":DASHBOARDS,
        "LIVE":dashboard["live"],
        "PROMOTION_ALLOWED":False,
        "EXPORT_READY":True
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return dashboard

if __name__=="__main__":
    print(json.dumps(build_dashboard(),indent=2,ensure_ascii=False))
