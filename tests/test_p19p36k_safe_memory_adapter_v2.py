from app.companionship.safe_recovery_adapter import (
    remember_user_message,
    recall_user_history,
    collect_memory_shadow,
)

def test_memory_adapter_v2_remember_and_recall():
    s = "+551111118001"
    assert remember_user_message(s, "quero emagrecer")
    assert remember_user_message(s, "tenho dor no joelho")
    hist = recall_user_history(s, 8)
    joined = " ".join(hist).lower()
    assert "emagrecer" in joined
    assert "joelho" in joined

def test_memory_adapter_v2_collect_shadow_context():
    s = "+551111118002"
    ctx = collect_memory_shadow(s, "quero abrir escola de inglês", {"active_domain": "general"})
    assert ctx["active_domain"] == "general"
    assert ctx["p19p36k_memory_shadow"]["remembered"] is True
    assert ctx["p19p36k_memory_shadow"]["history_count"] >= 1
