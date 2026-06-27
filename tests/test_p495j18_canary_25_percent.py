from app.api import whatsapp


def test_canary_percent_env_25(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "25")
    monkeypatch.delenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", raising=False)

    hits = 0
    total = 1000
    for i in range(total):
        if whatsapp._p495j16_recovery_canary_enabled(f"user-{i}"):
            hits += 1

    assert 200 <= hits <= 300


def test_canary_off_still_blocks_25(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "0")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "25")
    assert whatsapp._p495j16_recovery_canary_enabled("user-1") is False


def test_identity_response_under_25_allowlist(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "25")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", "sender-x")
    reply = whatsapp.eldora_primary_runtime_reply("sender-x", "como você chama?")
    assert "Eldora" in reply
