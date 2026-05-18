from app.api.whatsapp import eldora_primary_runtime_reply

def test_semantic_status():
    out = eldora_primary_runtime_reply("u","como esta ?").lower()
    assert "melhorando" in out

def test_semantic_failure():
    out = eldora_primary_runtime_reply("u","deu ruim").lower()
    assert "runtime novo" in out or "continuidade" in out
