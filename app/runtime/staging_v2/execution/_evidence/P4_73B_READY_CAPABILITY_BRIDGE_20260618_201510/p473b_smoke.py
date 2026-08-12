import json
from app.runtime.ready_capability_bridge import ready_capability_report

out = ready_capability_report(
    "whatsapp:+5519996166906",
    "P4.73B validar capabilities ready"
)

print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
print("P4.73B_SMOKE_COMPLETE")
