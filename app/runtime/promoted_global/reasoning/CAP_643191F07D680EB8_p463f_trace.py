import inspect
import traceback

print("PYTHON_UTF8_TRACE_OK")

def load(label, import_code):
    try:
        ns = {}
        exec(import_code, ns)
        print(f"IMPORT {label} OK")
        return ns
    except Exception:
        print(f"IMPORT {label} ERROR")
        print(traceback.format_exc())
        return {}

w = load("WHATSAPP", "from app.api.whatsapp import eldora_primary_runtime_reply")
c = load("COGNITIVE_PIPELINE", "from app.runtime.cognitive_pipeline import run_cognitive_pipeline")
r = load("ROUTE_FAST", "from app.runtime.intent_first_router import route_fast")
m = load("SHORT_MEMORY", "from app.runtime.short_memory import remember, recall")

eldora_primary_runtime_reply = w.get("eldora_primary_runtime_reply")
run_cognitive_pipeline = c.get("run_cognitive_pipeline")
route_fast = r.get("route_fast")
remember = m.get("remember")
recall = m.get("recall")

print("\n===== SIGNATURES =====")
for name, fn in [
    ("eldora_primary_runtime_reply", eldora_primary_runtime_reply),
    ("run_cognitive_pipeline", run_cognitive_pipeline),
    ("route_fast", route_fast),
    ("remember", remember),
    ("recall", recall),
]:
    if fn:
        try:
            print(name, inspect.signature(fn))
        except Exception as e:
            print(name, "SIGNATURE_ERROR", repr(e))

def safe(label, fn, *args, **kwargs):
    print("\n" + "=" * 90)
    print(label)
    print("=" * 90)
    if not fn:
        print("SKIPPED_FN_NOT_IMPORTED")
        return None
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

sender = "audit_p463f_root_ok"

cases = [
    "quero automatizar confinamento de boi",
    "e depois?",
    "quero criar plano estratégico da Eldora",
    "corrigir erro traceback no runtime",
    "estou ansioso e desanimado",
    "prosseguir evolução do mind",
]

print("\n===== MEMORY PRELOAD =====")
safe("remember(sender)", remember, sender, "ASSUNTO_ATIVO: confinamento de boi; proximo passo: agua, cocho, balanca e alertas")
safe("recall(sender)", recall, sender, limit=10)

print("\n===== ROUTE_FAST =====")
for msg in cases:
    safe("route_fast :: " + msg, route_fast, sender, msg)

print("\n===== COGNITIVE_PIPELINE =====")
for msg in cases:
    safe("run_cognitive_pipeline :: " + msg, run_cognitive_pipeline, sender, msg)

print("\n===== WHATSAPP_PRIMARY_RUNTIME =====")
for msg in cases:
    safe("eldora_primary_runtime_reply :: " + msg, eldora_primary_runtime_reply, sender, msg)

print("\n===== MEMORY AFTER =====")
safe("recall(sender)", recall, sender, limit=10)

print("\nP4.63F_RERUN_ROOT_OK_COMPLETE")
