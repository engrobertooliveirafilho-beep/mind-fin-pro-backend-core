from mind_trader.research.et665_r294_structural_pool_gate import audit_structural_pool

def row(i,f="F"):
    return {"candidate_id":str(i),"family_key":f,"pool_status":"DIVERSIFIED_SELECTED"}

def test_valid_structure_is_not_causal_certification():
    r=audit_structural_pool([row(1),row(2)])
    assert r["structural_constraints_pass"]
    assert not r["temporal_correlation_measured"]
    assert not r["runtime_promotion_allowed"]

def test_family_overallocation():
    r=audit_structural_pool([row(1),row(2),row(3)])
    assert "FAMILY_CAP_EXCEEDED" in r["issues"]

def test_duplicate_candidate():
    assert "MISSING_OR_DUPLICATE_CANDIDATE" in audit_structural_pool([row(1),row(1)])["issues"]

def test_pool_cap():
    assert "POOL_CAP_EXCEEDED" in audit_structural_pool([row(i,str(i)) for i in range(21)])["issues"]

def test_empty_pool():
    assert "EMPTY_POOL" in audit_structural_pool([])["issues"]
