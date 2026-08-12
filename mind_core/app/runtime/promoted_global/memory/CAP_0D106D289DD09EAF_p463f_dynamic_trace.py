import json
import inspect
import traceback

from app.api.whatsapp import eldora_primary_runtime_reply
from app.runtime.cognitive_pipeline import run_cognitive_pipeline

try:
    from app.runtime.intent_first_router import route_fast
except Exception as e:
    route_fast = None
    print("ROUTE_FAST_IMPORT_ERROR", repr(e))

try:
    from app.runtime.short_memory import remember, recall
except Exception as e:
    remember = None
    recall = None
    print("SHORT_MEMORY_IMPORT_ERROR", repr(e))

def safe_call(label, fn, *args, **kwargs):
    print("\n" + "=" * 90)
    print(label)
    print("=" * 90)
    try:
        out = fn(*args, **kwargs)
        print("TYPE:", type(out).__name__)
        print("VALUE:")
        print(str(out)[:3000])
        return out
    except Exception:
        print("ERROR:")
        print(traceback.format_exc())
        return None

print("\nPYTHON UTF8 TRACE OK")

print("\n===== FUNCTION SIGNATURES =====")
print("run_cognitive_pipeline:", inspect.signature(run_cognitive_pipeline))
if route_fast:
    print("route_fast:", inspect.signature(route_fast))
if remember:
    print("remember:", inspect.signature(remember))
if recall:
    print("recall:", inspect.signature(recall))

sender = "audit_p463f"

cases = [
    "quero automatizar confinamento de boi",
    "e depois?",
    "quero criar plano estratégico da Eldora",
    "corrigir erro traceback no runtime",
    "estou ansioso e desanimado",
]

print("\n===== SHORT MEMORY PRELOAD =====")
if remember:
    safe_call("remember(sender, contexto)", remember, sender, "ASSUNTO_ATIVO: confinamento de boi; próximo passo: água, cocho, balança e alertas")
if recall:
    safe_call("recall(sender)", recall, sender, limit=10)

print("\n===== ROUTE_FAST DIRECT =====")
if route_fast:
    for msg in cases:
        safe_call(f"route_fast({msg})", route_fast, sender, msg)

print("\n===== RUN_COGNITIVE_PIPELINE DIRECT =====")
for msg in cases:
    safe_call(f"run_cognitive_pipeline({msg})", run_cognitive_pipeline, sender, msg)

print("\n===== WHATSAPP PRIMARY RUNTIME =====")
for msg in cases:
    safe_call(f"eldora_primary_runtime_reply({msg})", eldora_primary_runtime_reply, sender, msg)

print("\n===== MEMORY AFTER =====")
if recall:
    safe_call("recall(sender)", recall, sender, limit=10)

print("\nP4.63F_DYNAMIC_TRACE_COMPLETE")
