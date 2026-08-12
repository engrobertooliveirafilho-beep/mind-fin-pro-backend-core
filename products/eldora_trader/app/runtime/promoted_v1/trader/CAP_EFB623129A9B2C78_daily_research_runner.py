import json, uuid
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.execution.paper_session import PaperTradingSessionManager
from mind_trader.app.orchestration.research_orchestrator import run_research_orchestrator
from mind_trader.app.audits.institutional_audit_ledger import append_audit_event, canonical_hash

def run_daily_research(symbols=("TEST",), timeframes=("1m",), db_path="mind_trader/data/market.sqlite", limit=10, ftmo_config_path="mind_trader/config/ftmo_ruleset.json"):
    daily_run_id=str(uuid.uuid4())
    start=datetime.now(UTC).isoformat()
    append_audit_event("P8.50_DAILY_RESEARCH_START",{"daily_run_id":daily_run_id,"symbols":symbols,"timeframes":timeframes})

    session=PaperTradingSessionManager(
        session_path="mind_trader/logs/P8.50_DAILY_PAPER_SESSION.json",
        ledger_path="mind_trader/logs/P8.50_DAILY_PAPER_LEDGER.jsonl",
        ftmo_config_path=ftmo_config_path
    )

    opened=session.open_session(account_id=f"PAPER_DAILY_{daily_run_id}")
    if opened["decision"]!="SESSION_OPENED":
        report={
            "daily_run_id":daily_run_id,
            "start_ts":start,
            "end_ts":datetime.now(UTC).isoformat(),
            "decision":"DAILY_RUN_ABORTED_SESSION_NOT_OPENED",
            "session_open":opened,
            "production":"BLOCKED",
            "live":"FORBIDDEN",
            "edge_claim":"NONE"
        }
        report["report_hash"]=canonical_hash(report)
        append_audit_event("P8.50_DAILY_RESEARCH_ABORTED",{"daily_run_id":daily_run_id,"reason":opened["decision"],"report_hash":report["report_hash"]})
        return report

    orchestration=run_research_orchestrator(symbols=symbols,timeframes=timeframes,db_path=db_path,limit=limit)
    closed=session.close_session(reason="DAILY_RESEARCH_COMPLETE")
    summary=session.daily_summary()

    report={
        "daily_run_id":daily_run_id,
        "start_ts":start,
        "end_ts":datetime.now(UTC).isoformat(),
        "session_open":opened,
        "orchestration":orchestration,
        "session_close":closed,
        "daily_summary":summary,
        "decision":"DAILY_RESEARCH_RUN_COMPLETE",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    report["report_hash"]=canonical_hash(report)
    final=append_audit_event("P8.50_DAILY_RESEARCH_FINALIZED",{"daily_run_id":daily_run_id,"report_hash":report["report_hash"],"decision":report["decision"]})
    report["ledger_hash"]=final["event_hash"]

    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.50_daily_research_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
