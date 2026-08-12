from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path

client = TestClient(app)

cases = [
    ("quero emagrecer", "+551199999801"),
    ("quais", "+551199999801"),
    ("como montar uma escola de inglês", "+551199999802"),
    ("quais", "+551199999802"),
    ("meu objetivo é passar na FTMO com a MIND", "+551199999803"),
    ("continue", "+551199999803"),
]

for body, sender in cases:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    print("SENDER:", sender)
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("OUT:", r.text[:900])
    print("-"*80)

telemetry = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")
print("TELEMETRY_EXISTS:", telemetry.exists())
if telemetry.exists():
    lines = telemetry.read_text(encoding="utf-8", errors="ignore").splitlines()
    print("TELEMETRY_LINES:", len(lines))
    print("LAST_TELEMETRY:", lines[-1][:1200] if lines else "")
