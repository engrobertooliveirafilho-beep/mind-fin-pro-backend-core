from app.runtime.conversation_maturity_runtime import mature_response
from app.runtime.provider_failover import failover_selftest

def test_self_critique_loop_reaches_90():
    r=mature_response("não entendi", "como resolver?")
    assert r["maturity_ready"] is True
    assert r["maturity_score"] >= 90
    assert "Execução" in r["output"]

def test_provider_failover_live_contract():
    r=failover_selftest()
    assert r["status"] == "ok"
    assert r["provider"] == "local_safe"
    assert len(r["errors"]) == 1
