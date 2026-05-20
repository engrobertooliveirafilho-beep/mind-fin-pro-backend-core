from app.api.whatsapp import eldora_primary_runtime_reply

def test_live_whatsapp_override_oi():
    out = eldora_primary_runtime_reply("u", "oi").lower()

    blocked = [
        "vamos resolver",
        "gargalo",
        "handler",
        "fallback",
        "runtime"
    ]

    assert any(x in out for x in ["oi", "tudo certo", "tudo bem"])
    assert not any(x in out for x in blocked)
