from app.api.whatsapp import eldora_primary_runtime_reply

def test_progress_question():
    out = eldora_primary_runtime_reply("u","e como esta indo?").lower()
    assert "melhorando" in out

def test_working_question():
    out = eldora_primary_runtime_reply("u","esta dando certo?").lower()
    assert "runtime novo" in out or "melhorando" in out

def test_join_message():
    out = eldora_primary_runtime_reply("u","getting-throughout").lower()
    assert "sandbox conectado" in out
