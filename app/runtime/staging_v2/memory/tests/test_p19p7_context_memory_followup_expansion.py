from app.api.whatsapp import _p19p7_contextual_followup_expansion

def test_p19p7_quais_sao_elas_expands_confinement_technologies():
    out = _p19p7_contextual_followup_expansion(
        "quais são elas?",
        "Para automatizar sua operação em confinamento de boi, considere as seguintes etapas práticas: Sensores e Monitoramento: Instale sensores de temperatura.",
        "automatizar toda minha operação em confinamento de boi"
    )
    assert "trato automatizado" in out.lower()
    assert "vagão" in out.lower() or "vagao" in out.lower()
    assert "cocho" in out.lower()
    assert "instale sensores de temperatura" not in out.lower()

def test_p19p7_explique_melhor_deepens_not_restart():
    out = _p19p7_contextual_followup_expansion(
        "explique melhor",
        "Para automatizar sua operação de confinamento de boi, considere os seguintes passos: Monitoramento de Ambiente: Instale sensores para medir temperatura.",
        "confinamento de boi automação alimentação trato cocho"
    )
    assert "começar pelo trato" in out.lower()
    assert "funcionário deixa de fazer tarefa repetitiva" in out.lower()
    assert "instale sensores para medir temperatura" not in out.lower()
