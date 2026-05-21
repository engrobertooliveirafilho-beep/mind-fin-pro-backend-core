
from app.runtime.factual_conversation_policy import apply_factual_conversation_policy

def test_removes_internal_cta():
    out=apply_factual_conversation_policy("Resumo. Digite APROFUNDAR para continuar.","CR250R pedal")
    assert "APROFUNDAR" not in out

def test_deepen_progresses_without_loop():
    a="IMS R$ 826,40. Menta R$ 1.099,00."
    out1=apply_factual_conversation_policy(a,"CR250R pedal","u1")
    out2=apply_factual_conversation_policy(a,"aprofundar","u1")
    assert out2 != out1
    assert len(out2) > 20

def test_compresses_whatsapp():
    out=apply_factual_conversation_policy("x"*1500,"CR250R pedal")
    assert len(out) <= 900
