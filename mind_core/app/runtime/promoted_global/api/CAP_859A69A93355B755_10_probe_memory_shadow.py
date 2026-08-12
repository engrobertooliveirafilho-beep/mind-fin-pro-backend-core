from fastapi.testclient import TestClient
from app.main import app
from app.companionship.safe_recovery_adapter import recall_user_history
from pathlib import Path
import json

client = TestClient(app)
sender = "+551199999901"

cases = [
    "quero emagrecer",
    "tenho dor no joelho",
    "quais",
    "prossiga",
]

for body in cases:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("OUT:", r.text[:900])
    print("-"*80)

hist = recall_user_history(sender, 8)
print("MEMORY_HISTORY:", hist)

telemetry = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")
print("TELEMETRY_EXISTS:", telemetry.exists())
if telemetry.exists():
    lines = telemetry.read_text(encoding="utf-8", errors="ignore").splitlines()
    print("TELEMETRY_LINES:", len(lines))
    for line in lines[-4:]:
        try:
            obj = json.loads(line)
            print("MEMORY_SHADOW:", obj.get("memory_shadow"))
        except Exception:
            print(line[:500])
