from app.api.whatsapp import eldora_primary_runtime_reply, _p19p16_confinement_domain_interceptor

def test_p19p16_direct_interceptor():
    out = _p19p16_confinement_domain_interceptor(
        "como posso automatizar meu confinamento de boi, para não precisar de funcionario?"
    )
    assert out is not None
    assert any(x in out.lower() for x in ["trato", "silo", "cocho", "bebedouro", "pesagem", "confinamento", "balança", "balanca"])
    assert "cocho" in out.lower()
    assert "silo" in out.lower()

def test_p19p16_first_turn_not_generic():
    out = eldora_primary_runtime_reply(
        "p19p16_case",
        "como posso automatizar meu confinamento de boi, para não precisar de funcionario?"
    )
    assert any(x in out.lower() for x in ["trato", "silo", "cocho", "bebedouro", "pesagem", "confinamento", "balança", "balanca"])
    assert "cocho" in out.lower()
    assert "organizar ideias" not in out.lower()
    assert "não tenho informação suficiente" not in out.lower()

def test_p19p16_followup_with_context_words():
    out = eldora_primary_runtime_reply(
        "p19p16_case_followup",
        "quero detalhes sobre confinamento de boi"
    )
    assert any(x in out.lower() for x in ["trato", "silo", "cocho", "bebedouro", "pesagem", "confinamento", "balança", "balanca"])
    assert "cocho" in out.lower()
