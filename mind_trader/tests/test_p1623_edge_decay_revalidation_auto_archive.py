from app.p1623_edge_decay_revalidation_auto_archive.engine import run, classify

def test_p1623_classify_blocks_live():
    e=classify({"profit_factor":2,"trades":40,"max_drawdown":0.1})
    assert e["LIVE"]=="FORBIDDEN"
    assert e["memory_status"] in ["ACTIVE_EDGE","WATCHLIST_DECAY","ARCHIVED_DECAY"]

def test_p1623_run():
    r=run()
    assert r["STATUS"]=="P16.23_EDGE_DECAY_REVALIDATION_AND_AUTO_ARCHIVE_IMPLEMENTED"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
