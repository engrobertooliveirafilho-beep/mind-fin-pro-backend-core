from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path
import json

client = TestClient(app)

sender1 = "+551199999906"
for body in ["quero emagrecer", "tenho dor no joelho", "quais exercícios?"]:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender1})
    print("FITNESS_INPUT:", body)
    print("OUT:", r.text[:700])
    print("-"*80)

sender2 = "+551199999907"
for body in ["como abrir empresa de software?"]:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender2})
    print("BUSINESS_INPUT:", body)
    print("OUT:", r.text[:700])
    print("-"*80)

telemetry = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")
lines = telemetry.read_text(encoding="utf-8", errors="ignore").splitlines() if telemetry.exists() else []
print("TELEMETRY_LINES:", len(lines))
for line in lines[-5:]:
    obj = json.loads(line)
    print("TEXT:", obj.get("text"))
    print("FUSION:", obj.get("memory_fusion_shadow"))
    print("ADVISOR:", obj.get("memory_fusion_advisor_shadow"))
    print("-"*80)
