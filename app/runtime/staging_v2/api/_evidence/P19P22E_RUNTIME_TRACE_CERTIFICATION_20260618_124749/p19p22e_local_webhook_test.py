from app.main import app
from fastapi.testclient import TestClient
from pathlib import Path

trace = Path("_evidence/P19P22E_LIVE_TRACE/runtime_trace.jsonl")
if trace.exists():
    trace.unlink()

client = TestClient(app)

cases = [
    {"From":"whatsapp:+5519999999999","Body":"como automatizar confinamento de boi?"},
    {"From":"whatsapp:+5519999999999","Body":"como eu faço?"},
    {"From":"whatsapp:+5519999999999","Body":"e depois?"},
]

for c in cases:
    r = client.post("/webhook/whatsapp", data=c)
    print("STATUS", r.status_code)
    print("BODY", r.text[:300].replace("\n"," "))

print("TRACE_EXISTS", trace.exists())
if trace.exists():
    print(trace.read_text(encoding="utf-8"))
