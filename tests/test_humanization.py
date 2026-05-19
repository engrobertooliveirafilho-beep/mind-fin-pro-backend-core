from app.humanization.human_conversation_runtime import human_reply,has_identity_leak,score_response
CASES=["o que achou da evolução?","vc está fazendo simulado?","acho você robótica","me explica derivadas","não gostei da resposta","tenho prova sexta","estou cansado","porque?","certeza?"]
def test_no_identity_leak_on_live_observed_cases():
    for c in CASES:
        r=human_reply(c)
        assert not has_identity_leak(r), (c,r)
def test_humanization_score_minimum():
    rows=[score_response(c,human_reply(c)) for c in CASES]
    assert sum(r["score"] for r in rows)/len(rows) >= 95
def test_identity_context_only():
    assert "Sou a Eldora" in human_reply("quem é você?")
    assert "Sou a Eldora" not in human_reply("vc está fazendo simulado?")
