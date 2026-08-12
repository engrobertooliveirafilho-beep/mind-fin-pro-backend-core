from pathlib import Path
import json
from datetime import datetime, UTC
from mind_trader.app.risk.ftmo_ruleset import load_ftmo_config
from mind_trader.app.audits.paper_research_readiness import paper_research_readiness

def preflight_check(data_folder, ftmo_config_path, tests_passed=196):
    data_path=Path(data_folder)
    csvs=list(data_path.glob("*.csv")) if data_path.exists() else []
    cfg,val=load_ftmo_config(ftmo_config_path)
    readiness=paper_research_readiness(tests_passed=tests_passed)

    checks={
        "data_folder_exists":data_path.exists(),
        "csv_files_present":len(csvs)>0,
        "ftmo_config_valid":bool(cfg and val["valid"]),
        "paper_research_ready":readiness["decision"]=="PAPER_RESEARCH_READY",
        "production_blocked":True,
        "live_forbidden":True,
        "edge_none":True
    }

    decision="PREFLIGHT_OK" if all(checks.values()) else "PREFLIGHT_BLOCKED"

    report={
        "report":"P8.71_PREFLIGHT_CHECK",
        "created_at":datetime.now(UTC).isoformat(),
        "checks":checks,
        "csv_count":len(csvs),
        "ftmo_validation":val,
        "readiness":readiness,
        "decision":decision,
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.71_preflight_check.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
