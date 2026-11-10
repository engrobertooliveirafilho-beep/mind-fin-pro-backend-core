from mind_trader.research.et665_r294_structural_pool_gate import audit_structural_pool

def row(i,f="F"):
    return {"candidate_id":str(i),"family_key":f,"pool_status":"DIVERSIFIED_SELECTED", "mode":"PAPER_ONLY", "real_orders":"FORBIDDEN", "ftmo_real":"FORBIDDEN", "real_execution_allowed":"False", "runtime_allowed":"False", "next_required":"P2403_CORRELATION_ANALYZER"}

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

def test_live_mode_is_denied():
    r=row(1);r["mode"]="LIVE"
    result=audit_structural_pool([r])
    assert "SAFETY_CONTRACT_INVALID" in result["issues"]
    assert result["runtime_promotion_allowed"] is False

def test_correlation_gate_cannot_be_skipped():
    r=row(1);r["next_required"]="NONE"
    result=audit_structural_pool([r])
    assert "CORRELATION_GATE_MISSING" in result["issues"]
