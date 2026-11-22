import pytest
from app.runtime.p2306_explainability_gate import reconcile_explainability

def sample():
    return {"signal_id":"P2302_5ed23464b49d","symbol":"GER40","timeframe":"H1",
            "action":"BUY","mode":"PAPER_ONLY","real_orders":"FORBIDDEN",
            "ftmo_real":"FORBIDDEN","consumption_status":"PENDING_MT5_CONSUMPTION",
            "confidence_score":"58","regime":"UNKNOWN_LIVE_REGIME_PENDING_FEATURE_READ",
            "session":"UNKNOWN_SESSION_PENDING_MT5_DATA","status":"NOT_BLOCKED"}

def test_historical_not_blocked_overridden():
    r=reconcile_explainability(sample())
    assert r["historical_decision"]=="NOT_BLOCKED"
    assert r["unknown_regime"] and r["unknown_session"]
    assert not r["signal_authorized"] and not r["e2e_certified"]

@pytest.mark.parametrize("field,bad",[("mode","LIVE"),("real_orders","ALLOWED"),
    ("ftmo_real","ALLOWED"),("consumption_status","FILLED"),
    ("confidence_score","101"),("confidence_score","NaN"),
    ("session",""),("signal_id","INVALID")])
def test_unsafe_explanation_rejected(field,bad):
    row=sample()
    row[field]=bad
    with pytest.raises(ValueError):reconcile_explainability(row)

def test_feature_annotation_cannot_certify():
    row=sample()
    row["regime"]="TREND"
    row["session"]="LONDON"
    r=reconcile_explainability(row,feature_evidence={"verified":True})
    assert not r["feature_provenance_verified"] and not r["signal_authorized"]
