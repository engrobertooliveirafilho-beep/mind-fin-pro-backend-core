from app.p1515_web_research_to_backtest_queue.engine import certified_datasets, build_queue, run

def test_p1515_certified_datasets_list():
    assert isinstance(certified_datasets(),list)

def test_p1515_queue_builds():
    q=build_queue()
    assert isinstance(q,list)
    assert all(x["real_orders"]=="FORBIDDEN" for x in q)

def test_p1515_manifest():
    m=run()
    assert m["STATUS"]=="P15.15_WEB_RESEARCH_TO_BACKTEST_QUEUE_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
