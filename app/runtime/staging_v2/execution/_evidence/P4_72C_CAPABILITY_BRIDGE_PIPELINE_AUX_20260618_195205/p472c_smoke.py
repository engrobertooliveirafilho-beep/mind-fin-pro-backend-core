from pathlib import Path
import os
import json

def load_env():
    p = Path(".env")
    if p.exists():
        for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

from app.runtime.capability_recovery_bridge import capability_recovery_report
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

print("===== BRIDGE REPORT =====")
bridge = capability_recovery_report("whatsapp:+5519996166906", "P4.72C validar capacidades")
print(json.dumps(bridge["summary"], ensure_ascii=False, indent=2))
for m in bridge["modules"]:
    print(m["module"], "import_ok=", m["import_ok"], "calls=", list(m.get("call_results", {}).keys()))

print("\n===== PIPELINE AUX TEST =====")
out = run_cognitive_pipeline(
    "whatsapp:+5519996166906",
    "Use retrieval e responda: qual é meu nome?"
)

print("ANSWER:", out.get("answer"))
print("HAS_CAPABILITIES:", "capabilities" in out)
print("CAP_SUMMARY:", (out.get("capabilities") or {}).get("summary"))
print("P4.72C_SMOKE_COMPLETE")
