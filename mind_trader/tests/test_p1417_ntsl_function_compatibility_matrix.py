from app.p1417_ntsl_function_compatibility_matrix.engine import read_nts_files, build_matrix, run

def test_p1417_reads_nts_files():
    assert isinstance(read_nts_files(), list)

def test_p1417_builds_matrix():
    m=build_matrix()
    assert len(m)>0
    assert any(x["function"]=="BuyAtMarket" for x in m)

def test_p1417_manifest():
    r=run()
    assert r["STATUS"]=="P14.17_NTSL_FUNCTION_COMPATIBILITY_MATRIX_IMPLEMENTED"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["EXPORT_READY"] is True
