from app.p1511_promoted_edge_forensic_audit.engine import run

def test_p1511():
    r=run()

    assert "FORENSIC_APPROVED" in r
    assert "TOP_10_EDGES" in r
