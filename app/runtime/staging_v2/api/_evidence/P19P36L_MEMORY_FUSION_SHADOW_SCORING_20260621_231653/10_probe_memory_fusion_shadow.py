from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path
import json

client = TestClient(app)
sender = "+551199999902"

for body in ["quero emagrecer", "tenho dor no joelho", "quais exercícios?", "prossiga"]:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("OUT:", r.text[:900])
    print("-"*80)

telemetry = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")
lines = telemetry.read_text(encoding="utf-8", errors="ignore").splitlines() if telemetry.exists() else []
print("TELEMETRY_LINES:", len(lines))
for line in lines[-4:]:
    obj = json.loads(line)
    print("MEMORY_SHADOW:", obj.get("memory_shadow"))
    print("FUSION_SHADOW:", obj.get("memory_fusion_shadow"))
