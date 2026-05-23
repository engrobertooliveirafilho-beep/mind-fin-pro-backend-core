
import json, os
from datetime import datetime, timezone
from pathlib import Path

TRACE_DIR = Path(os.getenv("MIND_FORENSIC_TRACE_DIR", "_evidence/WHATSAPP_RUNTIME_TRACE"))
TRACE_DIR.mkdir(parents=True, exist_ok=True)
TRACE_FILE = TRACE_DIR / "RUNTIME_PIPELINE_TRACE.jsonl"

def event(hop, **kw):
    payload = {
        "hop": hop,
        "sender_id": kw.get("sender_id"),
        "route": kw.get("route"),
        "module_name": kw.get("module_name"),
        "reply_before": str(kw.get("reply_before"))[:2000],
        "reply_after": str(kw.get("reply_after"))[:2000],
        "reasoning_mode": str(kw.get("reasoning_mode"))[:500],
        "aco_state": str(kw.get("aco_state"))[:500],
        "topic": str(kw.get("topic"))[:500],
        "intent": str(kw.get("intent"))[:500],
        "memory_hit": str(kw.get("memory_hit"))[:500],
        "factual_state": str(kw.get("factual_state"))[:500],
        "runtime_commit": os.getenv("RENDER_GIT_COMMIT") or os.getenv("COMMIT_SHA") or os.getenv("SOURCE_VERSION"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "extra": kw.get("extra", {}),
    }
    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return payload


def wrap_callable(module, name, hop):
    # compatibility stub for forensic audit
    # does NOT mutate runtime behavior
    return False
