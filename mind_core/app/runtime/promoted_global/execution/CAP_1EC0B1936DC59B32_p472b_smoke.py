import json
from app.runtime.capability_recovery_bridge import capability_recovery_report

out = capability_recovery_report(
    "whatsapp:+5519996166906",
    "P4.72B validar capacidades externas"
)

print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
print("P4.72B_SMOKE_COMPLETE")
