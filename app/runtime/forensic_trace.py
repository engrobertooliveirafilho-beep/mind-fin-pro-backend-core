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


def wrap_callable(fn, *args, **kwargs):
    return fn
