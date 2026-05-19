from app.dialogue.persona_consistency_guard import enforce
def test_persona_consistency():
    assert enforce("vamos seguir com as implantações")
    assert not enforce("Oi! Como posso ajudar?")
    assert not enforce("Eu sou a Eldora, camada conversacional do MIND")
