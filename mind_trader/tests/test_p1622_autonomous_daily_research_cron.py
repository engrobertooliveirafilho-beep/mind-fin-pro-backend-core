from app.p1622_autonomous_daily_research_cron.engine import run

def test_p1622_daily_cron_blocks_live():
    r=run()
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["MODE"]=="MANUAL_OR_OS_CRON"
