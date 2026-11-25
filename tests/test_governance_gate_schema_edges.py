import pytest
from app.mind_federation.policy import FederationContract, FederationPolicyEngine
from app.cog_treaty.treaty import CognitiveTreatyProtocol
from app.evolution_gatekeeper.core import EvolutionGatekeeper

@pytest.mark.parametrize("topic", [None, 1, {}, "   "])
def test_federation_rejects_invalid_topic(topic):
    engine = FederationPolicyEngine()
    engine.register_contract(FederationContract("remote", ["metrics"], 5))
    assert engine.can_share("remote", {"topic": topic, "sensitivity": 1})["allowed"] is False

def test_federation_rejects_non_mapping_payload():
    engine = FederationPolicyEngine()
    assert engine.can_share("remote", None)["allowed"] is False

@pytest.mark.parametrize("contract", [
    FederationContract("", ["metrics"], 5),
    FederationContract("remote", [], 5),
    FederationContract("remote", ["metrics", 7], 5),
])
def test_federation_rejects_malformed_contract(contract):
    with pytest.raises(ValueError):
        FederationPolicyEngine().register_contract(contract)

@pytest.mark.parametrize("parties", [[], ["a", "a"], ["a", 7], [" "]])
def test_treaty_rejects_invalid_parties(parties):
    result = CognitiveTreatyProtocol().negotiate(parties, {})
    assert result.status == "rejected"

@pytest.mark.parametrize("topics", ["metrics", [7], [" "]])
def test_treaty_rejects_invalid_topics(topics):
    result = CognitiveTreatyProtocol().negotiate(["a", "b"], {"topics": topics})
    assert result.status == "rejected"

@pytest.mark.parametrize("value", [True, "0.3"])
def test_evolution_rejects_boolean_and_string_scores(value):
    proposal = {"risk_score": .3, "alignment_score": .8, "redundancy_score": .2}
    proposal["risk_score"] = value
    with pytest.raises(ValueError):
        EvolutionGatekeeper().evaluate(proposal)
