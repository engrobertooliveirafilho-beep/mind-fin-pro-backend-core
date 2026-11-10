from mind_trader.research.et665_r301_replay_source_gate import check_replay_source

def check(name, **kwargs):
    return check_replay_source(name, source_kind="CAUSAL_STRATEGY_REPLAY", **kwargs)

def test_p2403b_historical_source_rejected_even_with_claims():
    r=check("p2403b_edge_trade_series.csv", causal_signal_verified=True, independent_ohlc_verified=True)
    assert "HISTORICAL_SOURCE_QUARANTINED" in r["issues"]
    assert not r["runtime_promotion_allowed"]

def test_p2403e_hash_scheduled_source_rejected():
    assert "HISTORICAL_SOURCE_QUARANTINED" in check("p2403e_de40_edge_trade_series.csv")["issues"]

def test_cycle_events_are_not_ohlc():
    assert "HISTORICAL_SOURCE_QUARANTINED" in check("de40_cycle_events.csv")["issues"]

def test_independent_provenance_is_required():
    r=check("new_replay.csv")
    assert "CAUSAL_SIGNAL_NOT_VERIFIED" in r["issues"]
    assert "OHLC_NOT_INDEPENDENTLY_VERIFIED" in r["issues"]

def test_preflight_does_not_certify():
    r=check("new_replay.csv", causal_signal_verified=True, independent_ohlc_verified=True)
    assert r["source_preflight_pass"]
    assert not r["temporal_correlation_certified"]
    assert not r["strategy_certified"]
    assert not r["runtime_promotion_allowed"]
