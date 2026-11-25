import json
from pathlib import Path
from app.p9_continuous_research_runtime.engine import run_cycle

DASHBOARDS = [
    "top_genomes", "top_dna", "top_datasets", "top_regimes",
    "top_robustness", "top_paper_candidates", "top_correlations",
    "uncertainty_alerts"
]

def build_dashboard():
    out = Path("reports/P9.7_RESEARCH_COMMAND_CENTER")
    out.mkdir(parents=True, exist_ok=True)
    cycle = run_cycle("P9.7_COMMAND_CENTER_BUILD")
    dashboard = {
        "status": "P9.7_BLOCKED_UPSTREAM_EVIDENCE_NOT_CERTIFIED",
        "dashboards": DASHBOARDS,
        "top_genomes": [],
        "top_paper_candidates": [],
        "top_datasets": [],
        "top_dna": [],
        "top_regimes": [],
        "top_robustness": [],
        "top_correlations": [],
        "uncertainty_alerts": [
            "REAL_DATA_LINEAGE_NOT_CERTIFIED",
            "P9_3_BACKTEST_EXECUTOR_NOT_CONNECTED",
            "WALK_FORWARD_NOT_EXECUTED",
            "MONTE_CARLO_NOT_EXECUTED",
            "ROBUSTNESS_COMMITTEE_NOT_EXECUTED",
            "PAPER_CANDIDATE_PROVENANCE_NOT_VERIFIED"
        ],
        "upstream_cycle_status": cycle["status"],
        "live": "FORBIDDEN",
        "production": "BLOCKED",
        "real_broker": "DISABLED",
        "ftmo_real": "FORBIDDEN",
        "promotion_allowed": False,
        "export_ready": False
    }
    (out / "P9.7_dashboard.json").write_text(
        json.dumps(dashboard, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    manifest = {
        "STATUS": dashboard["status"],
        "DASHBOARDS": DASHBOARDS,
        "LIVE": dashboard["live"],
        "PROMOTION_ALLOWED": False,
        "EXPORT_READY": False
    }
    (out / "P9.7_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return dashboard

if __name__ == "__main__":
    print(json.dumps(build_dashboard(), indent=2, ensure_ascii=False))
