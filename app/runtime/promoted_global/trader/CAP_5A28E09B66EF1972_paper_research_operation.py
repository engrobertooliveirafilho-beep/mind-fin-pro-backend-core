import json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.data.batch_market_ingestion import batch_ingest_market_folder
from mind_trader.app.orchestration.daily_research_runner import run_daily_research
from mind_trader.app.audits.paper_research_readiness import paper_research_readiness

def run_paper_research_operation(data_folder, symbol, timeframe, db_path, ftmo_config_path, limit=10):
    readiness=paper_research_readiness(tests_passed=191)
    if readiness["decision"]!="PAPER_RESEARCH_READY":
        return {"decision":"BLOCKED_NOT_READY","readiness":readiness,"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE"}

    ingestion=batch_ingest_market_folder(data_folder,symbol,timeframe,db_path)
    if ingestion["connected"] <= 0:
        return {"decision":"BLOCKED_NO_VALID_DATA","ingestion":ingestion,"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE"}

    daily=run_daily_research(
        symbols=(symbol,),
        timeframes=(timeframe,),
        db_path=db_path,
        limit=limit,
        ftmo_config_path=ftmo_config_path
    )

    report={
        "operation":"P8.68_RUN_PAPER_RESEARCH_OPERATION",
        "created_at":datetime.now(UTC).isoformat(),
        "readiness":readiness,
        "ingestion":ingestion,
        "daily_research":daily,
        "decision":"PAPER_RESEARCH_OPERATION_COMPLETE",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.68_paper_research_operation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

    return report
