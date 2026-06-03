
from app.runtime.conversation_state_machine import build_conversation_payload

def test_universal_vehicle_entity_state_without_brand_list():
    ctx={}
    build_conversation_payload("quero comprar uma RAM 2500 ano 2026", ctx)
    assert "ram 2500" in ctx["last_subject"]
    out=build_conversation_payload("quanto ela faz por litro?", ctx)
    assert "ASSUNTO ATUAL" in out
    assert "ram 2500" in out

def test_universal_non_vehicle_entity_state():
    ctx={}
    build_conversation_payload("quero montar um confinamento de boi para 200 boi por ciclo", ctx)
    assert "confinamento" in ctx["last_subject"]
    out=build_conversation_payload("seja mais especifico", ctx)
    assert "ASSUNTO ATUAL" in out
    assert "confinamento" in out
