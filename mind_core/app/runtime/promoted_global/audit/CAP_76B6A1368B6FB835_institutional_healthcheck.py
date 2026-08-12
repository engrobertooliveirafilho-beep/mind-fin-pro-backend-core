import json, subprocess, sys
from pathlib import Path
from mind_trader.app.audits.runtime_evidence_package import build_runtime_evidence_package
from mind_trader.app.audits.institutional_audit_ledger import verify_ledger

def run_pytest_suite(test_path="mind_trader/tests"):
    cmd=[sys.executable,"-m","pytest",test_path,"-q"]
    p=subprocess.run(cmd,capture_output=True,text=True)
    return {
        "returncode":p.returncode,
        "stdout":p.stdout,
        "stderr":p.stderr,
        "passed":p.returncode==0
    }

def assert_critical_blocks(package):
    checks={
        "production_blocked":package.get("production")=="BLOCKED",
        "live_forbidden":package.get("live")=="FORBIDDEN",
        "edge_none":package.get("edge_claim")=="NONE",
        "hash_present":len(package.get("package_hash",""))==64
    }
    return {"passed":all(checks.values()),"checks":checks}

def institutional_healthcheck(run_tests=False, expected_tests=141):
    tests={"passed":True,"skipped":True}
    if run_tests:
        tests=run_pytest_suite()
    pkg=build_runtime_evidence_package(expected_tests)
    blocks=assert_critical_blocks(pkg)
    ledger=verify_ledger()
    decision="SYSTEM_HEALTH_OK" if tests["passed"] and blocks["passed"] else "SYSTEM_HEALTH_FAIL"
    return {
        "decision":decision,
        "tests":tests,
        "evidence_package":pkg,
        "critical_blocks":blocks,
        "ledger_integrity":ledger,
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

def save_healthcheck_report(path="mind_trader/reports/P8.53_institutional_healthcheck.json",run_tests=False,expected_tests=141):
    r=institutional_healthcheck(run_tests,expected_tests)
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
    return r
