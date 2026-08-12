from app.p201_daily_demo_evidence_analyzer.engine import run

def test_p201():
    r=run()
    assert "STATUS" in r
