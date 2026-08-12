import json, uuid
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.genomes.strategy_genome import generate_strategy_genomes
from mind_trader.app.backtest.massive_cluster import massive_backtest_cluster
from mind_trader.app.engines.self_evolution import evolve_portfolio
from mind_trader.app.validation.validation_protocol_engine import validation_committee_report, REQUIRED_EVIDENCE
from mind_trader.app.audits.institutional_audit_ledger import append_audit_event, verify_ledger, institutional_snapshot, canonical_hash

def _extract_validation_reports(cluster):
    reports={}
    for r in cluster.get("ranking",[]):
        gid=r.get("genome_id")
        if gid and r.get("validation"):
            reports[gid]=r["validation"]
    return reports

def _committee_package():
    return {k: {"passed": False} for k in REQUIRED_EVIDENCE}

def run_research_orchestrator(symbols=("TEST",), timeframes=("1m",), db_path="mind_trader/data/market.sqlite", limit=10):
    run_id=str(uuid.uuid4())
    start=datetime.now(UTC).isoformat()
    append_audit_event("P8.44_RUN_START",{"run_id":run_id,"symbols":symbols,"timeframes":timeframes})

    genomes=generate_strategy_genomes(symbols=symbols,timeframes=timeframes)
    cluster=massive_backtest_cluster(genomes,db_path=db_path,limit=limit)
    validation_reports=_extract_validation_reports(cluster)
    evolution=evolve_portfolio(validation_reports) if validation_reports else {"evaluated":0,"ranked":[],"decision":"NO_VALIDATION_REPORTS"}

    committee=validation_committee_report(run_id,_committee_package())
    snapshot=institutional_snapshot(test_count=101)
    ledger_state=verify_ledger()

    report={
        "run_id":run_id,
        "start_ts":start,
        "end_ts":datetime.now(UTC).isoformat(),
        "symbols":list(symbols),
        "timeframes":list(timeframes),
        "genomes_total":len(genomes),
        "genomes_executed":cluster.get("executed",0),
        "genomes_tested":cluster.get("tested",0),
        "genomes_rejected":sum(1 for x in evolution.get("ranked",[]) if x.get("status") in ["REJECT_OR_RETEST","DEMOTED_RESEARCH_REVIEW"]),
        "genomes_research":sum(1 for x in evolution.get("ranked",[]) if x.get("status")=="KEEP_RESEARCH"),
        "genomes_paper":sum(1 for x in evolution.get("ranked",[]) if x.get("status")=="PAPER_CANDIDATE_ONLY"),
        "cluster":cluster,
        "self_evolution":evolution,
        "committee":committee,
        "snapshot":snapshot,
        "ledger_state":ledger_state,
        "decision":"RESEARCH_ORCHESTRATION_COMPLETE",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    report["snapshot_hash"]=canonical_hash(report)
    final_event=append_audit_event("P8.44_RUN_FINALIZED",{"run_id":run_id,"snapshot_hash":report["snapshot_hash"],"decision":report["decision"]})
    report["ledger_hash"]=final_event["event_hash"]
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.44_research_orchestrator_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
