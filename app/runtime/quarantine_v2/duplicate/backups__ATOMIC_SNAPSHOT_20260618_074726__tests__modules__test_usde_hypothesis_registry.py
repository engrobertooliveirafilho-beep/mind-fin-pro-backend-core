from app.modules.usde_core.hypothesis_registry import HypothesisRegistry

def test_hypothesis_registry():
    r=HypothesisRegistry()

    h=r.register(
        "markov_signal",
        "Markov transitions contain predictive information"
    )

    assert "hypothesis_id" in h
    assert r.count() >= 1
