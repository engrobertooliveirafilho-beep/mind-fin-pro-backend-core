import json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.validation.walk_forward_authority import walk_forward_authority
from mind_trader.app.validation.monte_carlo_authority import monte_carlo_authority
from mind_trader.app.validation.anti_overfitting_authority import anti_overfitting_authority
from mind_trader.app.engines.uncertainty_authority import uncertainty_score

def robustness_committee(genome_id, trades, walk_windows, param_results, validation_report):
    wf=walk_forward_authority(walk_windows)
    mc=monte_carlo_authority(trades,runs=200,max_dd_allowed=40)
    ao=anti_overfitting_authority(genome_id,trades,param_results)
    un=uncertainty_score(validation_report)

    passed = (
        wf.get("passed") is True and
        mc.get("passed") is True and
        ao.get("decision")=="ANTI_OVERFITTING_PASS_RESEARCH_ONLY" and
        un.get("decision")=="UNCERTAINTY_ACCEPT_RESEARCH"
    )

    report={
        "committee":"P8.83_ROBUSTNESS_COMMITTEE",
        "created_at":datetime.now(UTC).isoformat(),
        "genome_id":genome_id,
        "walk_forward":wf,
        "monte_carlo":mc,
        "anti_overfitting":ao,
        "uncertainty":un,
        "passed":passed,
        "decision":"ROBUSTNESS_PASS_PAPER_CANDIDATE" if passed else "ROBUSTNESS_REJECT_OR_RETEST",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.83_robustness_committee.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
