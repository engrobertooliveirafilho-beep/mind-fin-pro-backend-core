from app.api.whatsapp import eldora_primary_runtime_reply

def test_fuzzy_everything_good():
    out = eldora_primary_runtime_reply("u","tudo be?").lower()
    assert "melhorando" in out

def test_positive_confirmation():
    out = eldora_primary_runtime_reply("u","deu certo").lower()
    assert "continuidade" in out or "runtime" in out
