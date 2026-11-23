from pathlib import Path

from p2905_evolution_gate import classify_specialist, summarize


def test_high_proxy_values_do_not_certify():
    result = classify_specialist(5.0, 1.0)
    assert result["status"] == "UNVERIFIED_CANDIDATE"
    assert result["certification_basis"] == "BLOCKED_NO_INDEPENDENT_OOS_EVIDENCE"


def test_self_attested_oos_object_does_not_certify():
    result = classify_specialist(5.0, 1.0, {"status": "PASS", "sha256": "fake"})
    assert result["status"] == "UNVERIFIED_CANDIDATE"


def test_summary_never_promotes():
    result = summarize([{"payoff_proxy": 5, "stability_proxy": 1} for _ in range(45)])
    assert result["specialists"] == 45
    assert result["certified_core"] == 0
    assert result["unverified_candidates"] == 45


def test_chain_uses_the_p2905_gate():
    chain = Path(__file__).resolve().parents[1] / "mind_p2900_to_p2908_chain.py"
    source = chain.read_text(encoding="utf-8")
    assert "from p2905_evolution_gate import classify_specialist" in source
    assert "gate = classify_specialist(payoff, stability)" in source
    assert '"certified_core": 0' in source
