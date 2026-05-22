
from app.runtime.strategic_conversation_authority import strategic_conversation_authority

def test_fluency_priority_blocks_generic():
    out=strategic_conversation_authority("Tudo certo por aqui 🙂","quero melhorar a fluidez","u1")
    assert "fluidez conversacional" in out.lower()
    assert "tudo certo" not in out.lower()

def test_priority_followup_reuses_eldora_context():
    strategic_conversation_authority("base","Sobre Eldora, o que melhorar?","u2")
    out=strategic_conversation_authority("me dê mais contexto","o que fazer primeiro?","u2")
    assert "SCA" in out or "autoridade final" in out
