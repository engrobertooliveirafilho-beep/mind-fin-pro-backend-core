from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def send(body, sender):
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    assert r.status_code in (200, 201)
    return r.text.lower()

def test_webhook_hotfix_prevents_self_memory_false_positive():
    s = "+551111121003"
    send("como abrir empresa de software?", s)

    telemetry = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")
    assert telemetry.exists()
    txt = telemetry.read_text(encoding="utf-8", errors="ignore").lower()

    assert "current_message_excluded" in txt
    assert "memory_fusion_advisor_shadow" in txt
