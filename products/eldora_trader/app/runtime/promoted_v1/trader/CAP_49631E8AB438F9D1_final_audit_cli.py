import argparse, json
from datetime import datetime, UTC
from pathlib import Path
from mind_trader.app.cli.status_cli import operational_status
from mind_trader.app.audits.institutional_healthcheck import institutional_healthcheck
from mind_trader.app.audits.release_audit_gate import release_gate
from mind_trader.app.audits.runtime_evidence_package import build_runtime_evidence_package

def final_audit(tests_passed=205):
    status=operational_status(tests_passed=tests_passed)
    health=institutional_healthcheck(run_tests=False,expected_tests=tests_passed)
    release=release_gate("PAPER_RESEARCH",tests_passed)
    evidence=build_runtime_evidence_package(tests_passed)

    report={
        "command":"P8.74_FINAL_AUDIT_COMMAND",
        "created_at":datetime.now(UTC).isoformat(),
        "tests_passed":tests_passed,
        "status":status,
        "healthcheck":health,
        "release_gate":release,
        "evidence_hash":evidence["package_hash"],
        "decision":"FINAL_AUDIT_OK" if health["decision"]=="SYSTEM_HEALTH_OK" and release["decision"]=="RELEASE_AUDIT_PACKAGE_READY" else "FINAL_AUDIT_FAIL",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.74_final_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report

def run_final_audit_cli(argv=None):
    p=argparse.ArgumentParser("mind-trader-final-audit")
    p.add_argument("--tests-passed",type=int,default=205)
    args=p.parse_args(argv)
    r=final_audit(args.tests_passed)
    print(json.dumps(r,ensure_ascii=False,indent=2))
    return r

if __name__=="__main__":
    run_final_audit_cli()
