from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def send(body, sender):
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    assert r.status_code in (200, 201)
    return r.text.lower()

def test_shadow_adapter_does_not_break_reply():
    s = "+551111117001"
    a = send("quero emagrecer", s)
    b = send("quais", s)
    assert "peso" in b or "treino" in b or "cardio" in b

def test_shadow_adapter_generates_telemetry():
    s = "+551111117002"
    a = send("como montar uma escola de inglês", s)
    b = send("quais", s)
    telemetry = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")
    assert telemetry.exists()
    txt = telemetry.read_text(encoding="utf-8", errors="ignore")
    assert "+551111117002" in txt
    assert "recovered_shadow_context_count" in txt
