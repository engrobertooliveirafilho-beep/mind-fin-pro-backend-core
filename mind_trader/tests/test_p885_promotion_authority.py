from pathlib import Path
from mind_trader.app.validation.promotion_authority import promotion_authority

def test_blocks_live_promotion():
    r=promotion_authority("g1",{"decision":"PAPER_TRADING_APPROVED"},"LIVE")
    assert r["decision"]=="FORCE_BLOCK_PROMOTION"
    assert r["allowed"] is False
    assert r["production"]=="BLOCKED"
    assert r["live"]=="FORBIDDEN"

def test_promotes_only_to_paper_research():
    r=promotion_authority("g1",{"decision":"PAPER_TRADING_APPROVED"},"PAPER")
    assert r["decision"]=="PROMOTE_TO_PAPER_RESEARCH_ONLY"
    assert r["allowed"] is True
    assert r["edge_claim"]=="PAPER_RESEARCH_CANDIDATE_ONLY"

def test_rejects_unapproved_validation():
    r=promotion_authority("g1",{"decision":"REJECTED_EDGE"},"PAPER")
    assert r["decision"]=="PROMOTION_REJECTED"
    assert r["allowed"] is False

def test_promotion_report_written():
    promotion_authority("g1",{"decision":"PAPER_TRADING_APPROVED"},"PAPER")
    assert Path("mind_trader/reports/P8.85_promotion_authority.json").exists()
