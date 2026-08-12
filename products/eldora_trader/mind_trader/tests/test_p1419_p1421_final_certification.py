from app.p1419_p1421_final_certification.engine import promote, build_snapshot, run

def test_p1419_promote_returns_lists():
    p,r=promote()
    assert isinstance(p,list)
    assert isinstance(r,list)

def test_p1420_snapshot_blocks_live():
    s=build_snapshot()
    assert s["CERTIFICATION"]["REAL_ORDERS"]=="FORBIDDEN"
    assert s["EXPORT_READY"] is True

def test_p1421_final_certification():
    s=run()
    assert s["STATUS"]=="P14.21_MIND_TRADER_CORE_CERTIFIED"
    assert s["CERTIFICATION"]["PROFIT_NTSL_PIPELINE"]=="CERTIFIED"
