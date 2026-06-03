
from app.runtime.cognitive_style_composer import compose_human_style

def test_vehicle_provider_core_is_preserved():
    ctx={"last_domain":"vehicle_buying","last_subject":"RAM 2500 ano 2026"}
    r=compose_human_style("quanto ela faz por litro?","A RAM 2500 faz em média 6 a 8 km/l conforme uso.",ctx)
    assert "6 a 8 km/l" in r
    assert "pode ser uma boa compra" not in r.lower()

def test_empty_provider_still_has_safe_contextual_reply():
    ctx={"last_domain":"vehicle_buying","last_subject":"RAM 2500 ano 2026"}
    r=compose_human_style("vale a pena?","",ctx)
    assert "evidências" in r and "riscos" in r and "custos" in r

