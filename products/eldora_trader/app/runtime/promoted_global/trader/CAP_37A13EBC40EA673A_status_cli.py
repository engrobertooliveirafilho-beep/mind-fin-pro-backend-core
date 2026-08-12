import argparse, json
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.audits.paper_research_readiness import paper_research_readiness
from mind_trader.app.audits.preflight_check import preflight_check

def latest_reports(report_dir="mind_trader/reports", limit=10):
    p=Path(report_dir)
    if not p.exists():
        return []
    files=sorted(p.glob("*"), key=lambda x:x.stat().st_mtime, reverse=True)
    return [{"name":x.name,"path":str(x),"bytes":x.stat().st_size} for x in files[:limit]]

def operational_status(data_folder=None, ftmo_config=None, tests_passed=201):
    readiness=paper_research_readiness(tests_passed=tests_passed)
    preflight=None
    if data_folder and ftmo_config:
        preflight=preflight_check(data_folder,ftmo_config,tests_passed=tests_passed)
    return {
        "command":"P8.73_OPERATIONAL_STATUS",
        "created_at":datetime.now(UTC).isoformat(),
        "tests_passed":tests_passed,
        "readiness":readiness,
        "preflight":preflight,
        "latest_reports":latest_reports(),
        "decision":"STATUS_ONLY",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

def run_status_cli(argv=None):
    p=argparse.ArgumentParser("mind-trader-status")
    p.add_argument("--data-folder", default=None)
    p.add_argument("--ftmo-config", default=None)
    p.add_argument("--tests-passed", type=int, default=201)
    args=p.parse_args(argv)
    r=operational_status(args.data_folder,args.ftmo_config,args.tests_passed)
    print(json.dumps(r,ensure_ascii=False,indent=2))
    return r

if __name__=="__main__":
    run_status_cli()
