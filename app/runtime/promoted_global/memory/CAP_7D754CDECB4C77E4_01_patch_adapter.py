from pathlib import Path

p = Path("app/companionship/safe_recovery_adapter.py")
s = p.read_text(encoding="utf-8")

s = s.replace(
'''RECOVERED_MODULES = [
    # preenchido dinamicamente por auditoria futura, mantido vazio/seguro por padrão
]
''',
'''RECOVERED_MODULES = [
    "app.runtime.followup_unified_resolver",
    "app.runtime.generic_topic_memory_engine",
    "app.runtime.memory_adapter",
    "app.runtime.memory_store",
    "app.vision.vision_memory_store",
]
'''
)

if "P19P36H_SHADOW_TELEMETRY" not in s:
    s += r'''

# P19P36H_SHADOW_TELEMETRY
import json
from pathlib import Path
from datetime import datetime, timezone

TELEMETRY = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")

def _safe_json_default(obj):
    try:
        return str(obj)
    except Exception:
        return "<unserializable>"

def record_shadow_telemetry(sender: str, text: str, ctx: dict, reply: str) -> None:
    try:
        TELEMETRY.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": sender or "unknown",
            "text": (text or "")[:300],
            "active_domain": (ctx or {}).get("active_domain"),
            "active_subject": (ctx or {}).get("active_subject"),
            "recovered_shadow_context_count": len((ctx or {}).get("recovered_shadow_context", [])),
            "recovered_shadow_context": (ctx or {}).get("recovered_shadow_context", []),
            "reply_preview": (reply or "")[:300],
        }
        with TELEMETRY.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, default=_safe_json_default) + "\n")
    except Exception:
        pass
# /P19P36H_SHADOW_TELEMETRY
'''

p.write_text(s, encoding="utf-8")
print("P19P36H_ADAPTER_MODULES_AND_TELEMETRY_OK")
