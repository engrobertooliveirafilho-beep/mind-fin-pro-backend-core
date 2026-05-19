from app.dialogue.generic_llm_detector import detect,rewrite
def test_generic_llm_detector():
    assert detect("Como posso ajudar?")
    r=rewrite("o score pode significar várias coisas","implantações")
    assert "implanta" in r.lower()
