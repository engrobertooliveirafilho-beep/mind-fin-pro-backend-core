from __future__ import annotations
import json, os, uuid, time, traceback
from pathlib import Path

TRACE_DIR = Path("_evidence/runtime_real_hop_trace")
TRACE_DIR.mkdir(parents=True, exist_ok=True)

def new_trace(route,inbound_message,sender_id):
    return {
        "correlation_id": str(uuid.uuid4()),
        "created_at": time.time(),
        "route": route,
        "sender_id": sender_id,
        "inbound_message": inbound_message,
        "hops": {},
        "errors": []
    }

def mark(trace, hop, value):
    trace["hops"][hop] = {
        "type": type(value).__name__,
        "text": str(value)[:5000]
    }

def fail(trace, hop, exc):
    trace["errors"].append({
        "hop": hop,
        "error": repr(exc),
        "traceback": traceback.format_exc()[-5000:]
    })

def save(trace):
    p = TRACE_DIR / f"{trace['correlation_id']}.json"
    p.write_text(json.dumps(trace,ensure_ascii=False,indent=2),encoding="utf-8")
    return str(p)


def event(name, **kwargs):
    try:
        payload = {
            "event": name,
            "ts": time.time(),
            **kwargs
        }
        p = TRACE_DIR / "events.jsonl"
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass





# P19P28M_WRAP_CALLABLE_VARARGS
def wrap_callable(fn, *args, **kwargs):
    """
    Compatible idempotent wrapper.
    Accepts legacy signatures: wrap_callable(fn), wrap_callable(fn, name), wrap_callable(module, attr, fn).
    """
    if fn is None:
        return None

    target = fn
    name = None

    if len(args) >= 2 and callable(args[1]):
        target = args[1]
        name = str(args[0])
    elif len(args) >= 1:
        name = str(args[0])

    if getattr(target, "_p19p28m_wrapped", False):
        return target

    def _wrapped(*a, **k):
        try:
            event("P19P28M_WRAPPED_CALL", callable=name or getattr(target, "__name__", "unknown"))
        except Exception:
            pass
        return target(*a, **k)

    try:
        _wrapped.__name__ = getattr(target, "__name__", "_wrapped")
        _wrapped.__doc__ = getattr(target, "__doc__", None)
        _wrapped._p19p28m_wrapped = True
        _wrapped._p19p28m_original = target
    except Exception:
        pass

    return _wrapped
# /P19P28M_WRAP_CALLABLE_VARARGS
