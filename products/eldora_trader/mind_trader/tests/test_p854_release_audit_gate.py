from pathlib import Path
from mind_trader.app.audits.release_audit_gate import release_gate

def test_release_gate_blocks_live():
    r=release_gate("LIVE",145)
    assert r["decision"]=="FORCE_BLOCK_RELEASE"
    assert r["production"]=="BLOCKED"

def test_release_gate_generates_package():
    r=release_gate("PAPER_RESEARCH",145)
    assert r["decision"]=="RELEASE_AUDIT_PACKAGE_READY"
    assert r["allowed_scope"]=="PAPER_RESEARCH_ONLY"
    assert r["live"]=="FORBIDDEN"
    assert len(r["release_hash"])==64
    assert len(r["ledger_hash"])==64

def test_release_report_written():
    release_gate("PAPER_RESEARCH",145)
    assert Path("mind_trader/reports/P8.54_release_audit_gate.json").exists()
