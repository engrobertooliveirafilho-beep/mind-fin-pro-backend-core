from app.p1621o_edge_factory_master_certification.engine import run

def test_p1621o_master_certification_blocks_live():
    r=run()
    assert r["STATUS"]=="P16.21O_EDGE_FACTORY_MASTER_CERTIFIED"
    assert r["CERTIFICATION"]=="PAPER_RESEARCH_CERTIFIED"
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
