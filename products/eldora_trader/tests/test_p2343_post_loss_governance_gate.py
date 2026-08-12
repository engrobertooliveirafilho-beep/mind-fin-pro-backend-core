from app.runtime.p2343_post_loss_governance_gate import post_loss_gate, health

def test_post_loss_blocks_when_context_fails():
    out = post_loss_gate("EURUSD", "BUY", True, {"m1": True})
    assert out["status"] == "BLOCKED"
    assert out["real_orders"] == "FORBIDDEN"

def test_post_loss_approves_when_context_passes():
    out = post_loss_gate("EURUSD", "BUY", True, {
        "m1": True, "m5": True, "m15": True, "h1": True,
        "trend_filter": True, "volatility_filter": True,
        "session_filter": True, "support_resistance_filter": True
    })
    assert out["status"] == "APPROVED"

def test_health():
    assert health()["status"] == "OK"
