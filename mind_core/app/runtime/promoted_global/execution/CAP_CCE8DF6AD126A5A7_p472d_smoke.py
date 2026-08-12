import json
from app.runtime.capability_recovery_bridge import capability_recovery_report

out = capability_recovery_report(
    "whatsapp:+5519996166906",
    "P4.72D async safe validation"
)

print(json.dumps(out["summary"], ensure_ascii=False, indent=2))
for m in out["modules"]:
    print(m["module"], m.get("call_results", {}))

print("P4.72D_SMOKE_COMPLETE")
