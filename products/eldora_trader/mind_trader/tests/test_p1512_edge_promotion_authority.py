from app.p1512_edge_promotion_authority.engine import authority, run

def test_p1512_authority_list():
    assert isinstance(authority(),list)

def test_p1512_manifest_blocks_live():
    m=run()
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
