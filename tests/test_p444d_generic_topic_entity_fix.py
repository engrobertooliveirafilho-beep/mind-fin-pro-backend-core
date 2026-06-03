
from app.runtime.generic_topic_memory_engine import update_topic_context, expand_followup

def test_ram_subject_is_vehicle_buying_and_followup_expands():
    ctx={}
    update_topic_context("quero comprar uma RAM 2500 ano 2026", ctx)
    assert ctx["last_domain"]=="vehicle_buying"
    assert "RAM" in ctx["last_subject"].upper()
    out=expand_followup("quanto ela faz por litro?", ctx)
    assert "RAM" in out.upper()
    assert "compra de veículo usado" in out

def test_corolla_crf_followup_expands():
    for msg in ["quero comprar um Corolla", "quero comprar uma CRF 450"]:
        ctx={}
        update_topic_context(msg, ctx)
        assert ctx["last_domain"]=="vehicle_buying"
        assert "Contexto obrigatório" in expand_followup("vale a pena", ctx)
