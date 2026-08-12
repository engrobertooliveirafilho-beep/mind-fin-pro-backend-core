from app.p1621n_continuous_youtube_loop_scheduler.engine import run

def test_p1621n_scheduler_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21N_CONTINUOUS_YOUTUBE_LOOP_SCHEDULER_IMPLEMENTED"
    assert "REAL_ORDERS" in r["NEVER_EXECUTE"]
    assert r["LIVE"]=="FORBIDDEN"
