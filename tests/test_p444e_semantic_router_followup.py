
from app.runtime.semantic_router import semantic_route

def test_semantic_router_promotes_referential_followups_with_subject():
    ctx={"last_subject":"compra de veículo usado: ram 2500 ano 2026","last_domain":"vehicle_buying"}
    for msg in ["quanto ela faz por litro?","vale a pena?","e a manutenção?","consumo","pontos fracos"]:
        d=semantic_route(msg,ctx)
        assert d.intent=="FOLLOWUP"
        assert d.domain=="vehicle_buying"

def test_semantic_router_does_not_force_followup_without_subject():
    d=semantic_route("quanto ela faz por litro?",{})
    assert d.intent!="FOLLOWUP"
