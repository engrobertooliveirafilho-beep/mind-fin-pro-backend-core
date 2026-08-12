from pathlib import Path
from mind_trader.app.audits.paper_research_v1_release import paper_research_v1_release

def test_paper_research_v1_release():
    r=paper_research_v1_release(298)
    assert r["release"]=="P8.100_PAPER_RESEARCH_V1"
    assert r["decision"]=="PAPER_RESEARCH_V1_CERTIFIED"
    assert r["validated_scope"]=="PAPER_RESEARCH_ONLY"
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"
    assert r["real_broker_routing"]=="DISABLED"
    assert r["edge_claim"]=="NONE"
    assert len(r["release_hash"])==64

def test_paper_research_v1_report_written():
    paper_research_v1_release(298)
    assert Path("mind_trader/reports/P8.100_paper_research_v1_release.json").exists()
