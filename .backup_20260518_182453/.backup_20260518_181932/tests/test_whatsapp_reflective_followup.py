from app.api.whatsapp import eldora_primary_runtime_reply

def test_explain_better():
    out = eldora_primary_runtime_reply("u","nao entendi").lower()
    assert "três camadas" in out or "tres camadas" in out
    assert "frases genéricas" in out or "frases genericas" in out

def test_deepen():
    out = eldora_primary_runtime_reply("u","aprofunde").lower()
    assert "memória contextual" in out or "memoria contextual" in out

def test_detail_better():
    out = eldora_primary_runtime_reply("u","detalhe melhor").lower()
    assert "cognição profunda" in out or "cognicao profunda" in out

