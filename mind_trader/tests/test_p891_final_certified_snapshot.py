from pathlib import Path
from mind_trader.app.audits.final_certified_snapshot import freeze_final_snapshot

def test_freeze_final_snapshot():
    r=freeze_final_snapshot(270)
    assert r["snapshot"]=="P8.91_FINAL_CERTIFIED_RESEARCH_SNAPSHOT"
    assert r["decision"]=="CERTIFIED_FOR_PAPER_RESEARCH_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["edge_claim"]=="NONE"
    assert len(r["snapshot_hash"])==64

def test_final_snapshot_report_written():
    freeze_final_snapshot(270)
    assert Path("mind_trader/reports/P8.91_final_certified_snapshot.json").exists()
