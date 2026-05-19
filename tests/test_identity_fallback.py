from app.humanization.human_conversation_runtime import human_reply,has_identity_leak
def test_identity_fallback_blocked():
    prompts=["o que achou da evolução?","vc esta fazendo simulado?","não gostei da resposta","porque?","cadê a resposta?"]
    for p in prompts:
        assert not has_identity_leak(human_reply(p))
def test_reflective_dialogue_keywords():
    assert "gargalo" in human_reply("porque?").lower()
    assert "simulações" in human_reply("vc está fazendo simulado?").lower() or "simulacoes" in human_reply("vc está fazendo simulado?").lower()
