from app.companionship.safe_recovery_adapter import collect_recovered_context, enrich_reply_shadow

def test_safe_recovery_adapter_shadow_no_mutation():
    ctx = {"active_domain": "fitness"}
    out = collect_recovered_context("+TEST", "quero emagrecer", ctx)
    assert out["active_domain"] == "fitness"
    assert "recovered_shadow_context" in out
    reply = enrich_reply_shadow("+TEST", "quero emagrecer", out, "base")
    assert reply == "base"
