from app.api.whatsapp import eldora_primary_runtime_reply

def test_semantic_plan():
    out = eldora_primary_runtime_reply("u","qual o plano?").lower()
    assert "estabilizar" in out

def test_semantic_how_to():
    out = eldora_primary_runtime_reply("u","e como fazer?").lower()
    assert "memoria contextual" in out or "estabilizar" in out
