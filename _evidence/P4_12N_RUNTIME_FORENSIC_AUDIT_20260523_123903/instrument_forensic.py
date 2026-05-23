from pathlib import Path
import re, textwrap

repo=Path.cwd()
audit=repo / "_evidence" / [p.name for p in (repo/"_evidence").glob("P4_12N_RUNTIME_FORENSIC_AUDIT_*")][-1]

trace_py = r'''
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
'''
(repo/"app/runtime/forensic_trace.py").write_text(trace_py, encoding="utf-8")

bootstrap = r'''
import importlib
from app.runtime.forensic_trace import event, wrap_callable

TARGETS = [
    ("app.runtime.live_whatsapp_response", ["eldora_primary_runtime_reply", "live_whatsapp_response"]),
    ("app.runtime.universal_conversation_authority", ["universal_conversation_authority", "apply_universal_conversation_authority"]),
    ("app.runtime.factual_search_handoff", ["factual_search_handoff", "apply_factual_search_handoff"]),
    ("app.runtime.whatsapp_final_output_guard", ["whatsapp_final_output_guard", "apply_whatsapp_final_output_guard"]),
    ("app.runtime.final_conversational_arbiter", ["final_conversational_arbiter", "apply_final_conversational_arbiter"]),
    ("app.runtime.generic_conversation_state", ["get_state", "set_state", "clear_state"]),
    ("app.api.whatsapp", ["twiml", "webhook", "whatsapp_webhook"]),
]

def install():
    wrapped = []
    for mod_name, names in TARGETS:
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            event("FORENSIC_IMPORT_FAIL", module_name=mod_name, reply_after=repr(e))
            continue
        for name in names:
            if wrap_callable(mod, name, name.upper()):
                wrapped.append(f"{mod_name}.{name}")
    event("FORENSIC_BOOTSTRAP_INSTALLED", reply_after=wrapped, extra={"wrapped_count": len(wrapped)})
    return wrapped
'''
(repo/"app/runtime/forensic_bootstrap.py").write_text(bootstrap, encoding="utf-8")

main = repo/"app/main.py"
txt = main.read_text(encoding="utf-8")
if "forensic_bootstrap.install()" not in txt:
    insert = "\n# P4.12N forensic observability only: no cognitive guard, no reply mutation\ntry:\n    from app.runtime import forensic_bootstrap\n    forensic_bootstrap.install()\nexcept Exception as _mind_forensic_error:\n    print('MIND_FORENSIC_BOOTSTRAP_ERROR', repr(_mind_forensic_error))\n"
    txt = insert + "\n" + txt
    main.write_text(txt, encoding="utf-8")

wa = repo/"app/api/whatsapp.py"
w = wa.read_text(encoding="utf-8")
if "REQUEST_IN" not in w:
    w = w.replace("from fastapi", "from app.runtime.forensic_trace import event\nfrom fastapi", 1) if "from fastapi" in w else "from app.runtime.forensic_trace import event\n" + w
    w = re.sub(r'(async\s+def\s+\w*webhook\w*\s*\([^)]*\)\s*:)', r"\1\n    event('REQUEST_IN', route='/webhook/whatsapp', module_name='app.api.whatsapp')", w, count=1)
    w = re.sub(r'(def\s+twiml\s*\(\s*message\s*:\s*str\s*\)\s*->\s*str\s*:)', r"\1\n    event('PRE_TWIML', route='/webhook/whatsapp', module_name='app.api.whatsapp', reply_before=message)", w, count=1)
    w = re.sub(r'(return\s+f[\'\"].*?<Message>\{safe\}</Message>.*?[\'\"])', r"event('TWIML_OUT', route='/webhook/whatsapp', module_name='app.api.whatsapp', reply_after=safe)\n    \1", w, count=1, flags=re.S)
    wa.write_text(w, encoding="utf-8")

print("FORENSIC_PATCH_DONE")
