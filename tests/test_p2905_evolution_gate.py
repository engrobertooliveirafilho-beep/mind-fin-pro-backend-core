from p2905_evolution_gate import classify_specialist, summarize

def test_high_proxy_values_do_not_certify():
    r = classify_specialist(5.0, 1.0)
    assert r["status"] == "UNVERIFIED_CANDIDATE"
    assert r["certification_basis"] == "BLOCKED_NO_INDEPENDENT_OOS_EVIDENCE"

def test_self_attested_oos_object_does_not_certify():
    r = classify_specialist(5.0, 1.0, {"status":"PASS","sha256":"fake"})
    assert r["status"] == "UNVERIFIED_CANDIDATE"

def test_summary_never_promotes():
    r = summarize([{"payoff_proxy":5,"stability_proxy":1} for _ in range(45)])
    assert r["specialists"] == 45
    assert r["certified_core"] == 0
    assert r["unverified_candidates"] == 45
