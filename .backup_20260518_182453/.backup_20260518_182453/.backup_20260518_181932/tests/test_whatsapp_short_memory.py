from app.api.whatsapp import eldora_primary_runtime_reply

def test_followup_conseguiu():
    eldora_primary_runtime_reply("u","nao esta funcionando")
    out = eldora_primary_runtime_reply("u","conseguiu?").lower()
    assert "continuidade" in out or "natural" in out

def test_followup_parece_nao():
    eldora_primary_runtime_reply("u","o que fazer?")
    out = eldora_primary_runtime_reply("u","parece que nao").lower()
    assert "contexto" in out or "generica" in out or "genérica" in out
