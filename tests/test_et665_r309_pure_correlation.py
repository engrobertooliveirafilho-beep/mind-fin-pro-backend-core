from mind_trader.research.et665_r309_pure_correlation import analyze_paper_series

def rows():
    return [
        {"edge_id":"A","timestamp":str(i),"pnl_r":float(i)}
        for i in range(1,5)
    ] + [
        {"edge_id":"B","timestamp":str(i),"pnl_r":float(i*2)}
        for i in range(1,5)
    ]

def test_valid_pair_not_certified():
    r=analyze_paper_series(rows())
    assert r["analysis_valid"] and len(r["pairs"])==1
    assert abs(r["pairs"][0]["pearson"]-1)<1e-12
    assert not r["correlation_certified"] and not r["runtime_promotion_allowed"]

def test_duplicate_rejected():
    data=rows()
    data.append(data[0].copy())
    assert "DUPLICATE_EDGE_TIMESTAMP" in analyze_paper_series(data)["issues"]

def test_nonfinite_rejected():
    data=rows()
    data[0]["pnl_r"]=float("nan")
    assert "INVALID_PNL" in analyze_paper_series(data)["issues"]

def test_malformed_rejected():
    assert "MALFORMED_ROW" in analyze_paper_series([None])["issues"]

def test_empty_rejected():
    assert "INSUFFICIENT_EDGES" in analyze_paper_series([])["issues"]

def test_constant_series_not_misrepresented_as_zero_correlation():
    data=rows()
    for r in data:
        if r["edge_id"]=="B":
            r["pnl_r"]=1.0
    result=analyze_paper_series(data)
    assert result["pairs"][0]["pearson"] is None
