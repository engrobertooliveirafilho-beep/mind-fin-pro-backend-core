import pytest
from app.mind_federation.policy import FederationContract, FederationPolicyEngine
from app.cog_treaty.treaty import CognitiveTreatyProtocol
from app.evolution_gatekeeper.core import EvolutionGatekeeper

@pytest.mark.parametrize("value", [None, -1, 11, True, 1.5, "2"])
def test_federation_invalid_sensitivity_is_denied(value):
    engine = FederationPolicyEngine()
    engine.register_contract(FederationContract("b", ["metrics"], 5))
    assert not engine.can_share("b", {"topic": "metrics", "sensitivity": value})["allowed"]

def test_federation_contract_isolated_from_external_mutation():
    engine = FederationPolicyEngine()
    contract = FederationContract("b", ["metrics"], 5)
    engine.register_contract(contract)
    contract.max_sensitivity = 10
    engine.get_contract("b").allowed_topics.append("secret")
    assert not engine.can_share("b", {"topic": "metrics", "sensitivity": 6})["allowed"]
    assert not engine.can_share("b", {"topic": "secret", "sensitivity": 0})["allowed"]
    assert engine.can_share("b", {"topic": "metrics", "sensitivity": 5})["allowed"]

@pytest.mark.parametrize("value", [None, -1, 11, True, 1.5, "2"])
def test_treaty_invalid_sensitivity_is_rejected(value):
    result = CognitiveTreatyProtocol().negotiate(
        ["a", "b"], {"max_data_sensitivity": value}
    )
    assert result.status == "rejected"

@pytest.mark.parametrize("key", ["risk_score", "alignment_score", "redundancy_score"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, 2])
def test_evolution_invalid_scores_are_rejected(key, value):
    proposal = {"risk_score": .3, "alignment_score": .8, "redundancy_score": .2}
    proposal[key] = value
    with pytest.raises(ValueError):
        EvolutionGatekeeper().evaluate(proposal)

@pytest.mark.parametrize("key", ["risk_score", "alignment_score", "redundancy_score"])
def test_evolution_missing_scores_fail_closed(key):
    proposal = {"risk_score": .3, "alignment_score": .8, "redundancy_score": .2}
    del proposal[key]
    with pytest.raises(KeyError):
        EvolutionGatekeeper().evaluate(proposal)
