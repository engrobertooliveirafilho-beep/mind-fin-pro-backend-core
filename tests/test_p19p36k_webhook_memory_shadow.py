from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def send(body, sender):
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    assert r.status_code in (200, 201)
    return r.text.lower()

def test_webhook_memory_shadow_records_history():
    s = "+551111118003"
    a = send("quero emagrecer", s)
    b = send("tenho dor no joelho", s)
    c = send("quais", s)

    telemetry = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")
    assert telemetry.exists()
    txt = telemetry.read_text(encoding="utf-8", errors="ignore").lower()
    assert "memory_shadow" in txt
    assert "history_count" in txt
    assert "joelho" in txt or "emagrecer" in txt
