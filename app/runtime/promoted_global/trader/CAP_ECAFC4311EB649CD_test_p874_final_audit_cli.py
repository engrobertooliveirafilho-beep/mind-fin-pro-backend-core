from pathlib import Path
from mind_trader.app.cli.final_audit_cli import final_audit, run_final_audit_cli

def test_final_audit_ok():
    r=final_audit(205)
    assert r["decision"]=="FINAL_AUDIT_OK"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"

def test_final_audit_cli_runs():
    r=run_final_audit_cli(["--tests-passed","205"])
    assert r["decision"]=="FINAL_AUDIT_OK"

def test_final_audit_report_written():
    final_audit(205)
    assert Path("mind_trader/reports/P8.74_final_audit.json").exists()
