
import json, os, time, traceback
from pathlib import Path
from datetime import datetime, timezone

TRACE_DIR = Path(os.getenv("MIND_FORENSIC_TRACE_DIR", "_evidence/WHATSAPP_RUNTIME_TRACE"))
TRACE_DIR.mkdir(parents=True, exist_ok=True)
TRACE_FILE = TRACE_DIR / "RUNTIME_PIPELINE_TRACE.jsonl"

def _now():
    return datetime.now(timezone.utc).isoformat()

def _short(x):
    try:
        s = str(x)
    except Exception:
        s = repr(x)
    return s[:2000]

def event(hop, **kw):
    payload = {
        "hop": hop,
        "sender_id": kw.get("sender_id"),
        "route": kw.get("route"),
        "module_name": kw.get("module_name"),
        "reply_before": _short(kw.get("reply_before")),
        "reply_after": _short(kw.get("reply_after")),
        "reasoning_mode": _short(kw.get("reasoning_mode")),
        "aco_state": _short(kw.get("aco_state")),
        "topic": _short(kw.get("topic")),
        "intent": _short(kw.get("intent")),
        "memory_hit": _short(kw.get("memory_hit")),
        "factual_state": _short(kw.get("factual_state")),
        "runtime_commit": os.getenv("RENDER_GIT_COMMIT") or os.getenv("COMMIT_SHA") or os.getenv("SOURCE_VERSION"),
        "timestamp": _now(),
        "extra": kw.get("extra", {}),
    }
    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return payload

def wrap_callable(module, name, hop):
    fn = getattr(module, name, None)
    if not callable(fn) or getattr(fn, "_mind_forensic_wrapped", False):
        return False
    def wrapper(*args, **kwargs):
        before = args[0] if args else kwargs
        event(hop + "_IN", module_name=getattr(module, "__name__", ""), reply_before=before, extra={"function": name})
        try:
            out = fn(*args, **kwargs)
            event(hop + "_OUT", module_name=getattr(module, "__name__", ""), reply_before=before, reply_after=out, extra={"function": name})
            return out
        except Exception as e:
            event(hop + "_ERROR", module_name=getattr(module, "__name__", ""), reply_before=before, reply_after=repr(e), extra={"function": name, "traceback": traceback.format_exc()})
            raise
    wrapper._mind_forensic_wrapped = True
    setattr(module, name, wrapper)
    return True
