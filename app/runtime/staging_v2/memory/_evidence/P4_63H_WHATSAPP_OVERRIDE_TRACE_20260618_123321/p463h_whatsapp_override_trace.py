import os
import json
import traceback
import inspect

from app.runtime.short_memory import remember, recall
from app.runtime.cognitive_pipeline import run_cognitive_pipeline
import app.api.whatsapp as w

print("P4.63H_START")
print("whatsapp module:", w.__file__)
print("eldora_primary_runtime_reply:", inspect.signature(w.eldora_primary_runtime_reply))

sender_cases = {
    "A_CONFINAMENTO": {
        "sender": "p463h_A_confinamento",
        "memory": "ASSUNTO_ATIVO=confinamento de boi; foco=água, cocho, balança, trato, sensores, alertas"
    },
    "B_ELDORA": {
        "sender": "p463h_B_eldora",
        "memory": "ASSUNTO_ATIVO=lançamento Eldora; foco=persona, WhatsApp, aquisição, retenção, canary"
    },
    "C_DEBUG": {
        "sender": "p463h_C_debug",
        "memory": "ASSUNTO_ATIVO=debug runtime; foco=traceback, pytest, app/main.py, cognitive_pipeline, evidência"
    }
}

inputs = [
    "e depois?",
    "como fazer?",
    "prossiga",
    "qual próximo passo?",
    "quero automatizar confinamento de boi",
    "quero criar plano estratégico da Eldora",
]

for label, cfg in sender_cases.items():
    remember("active_context", cfg["memory"], sender_id=cfg["sender"])
    print("MEMORY_SET", label, recall("active_context", sender_id=cfg["sender"]))

# Monkeypatch run_cognitive_pipeline usado dentro do módulo whatsapp
original_pipeline = w.run_cognitive_pipeline

def traced_pipeline(sender_id, message):
    print("\n--- PIPELINE_CALLED_FROM_WHATSAPP ---")
    print("sender_id:", sender_id)
    print("message:", message[:1000])
    result = original_pipeline(sender_id, message)
    print("pipeline_answer:", str(result.get("answer", result))[:1000] if isinstance(result, dict) else str(result)[:1000])
    print("pipeline_intent:", result.get("intent") if isinstance(result, dict) else None)
    return result

w.run_cognitive_pipeline = traced_pipeline

# Monkeypatch guards principais para rastrear alteração de resposta
guards = [
    "_p19p9_universal_whatsapp_output_guard",
    "_p19p8_suppress_generic_restart",
    "_p19p7_contextual_followup_expansion",
    "_p19p6_expand_bad_followup_template",
    "_p19p5_block_agricultural_automotive_contamination",
]

originals = {}

for name in guards:
    if hasattr(w, name):
        originals[name] = getattr(w, name)

        def make_wrapper(n, fn):
            def wrapper(*args, **kwargs):
                before = args[1] if len(args) > 1 else ""
                out = fn(*args, **kwargs)
                print("\n--- GUARD_CALL:", n, "---")
                print("before:", str(before)[:500])
                print("after :", str(out)[:500])
                print("changed:", str(before) != str(out))
                return out
            return wrapper

        setattr(w, name, make_wrapper(name, getattr(w, name)))

results = {}

for msg in inputs:
    print("\n" + "=" * 100)
    print("INPUT:", msg)
    print("=" * 100)

    results[msg] = {}

    for label, cfg in sender_cases.items():
        sender = cfg["sender"]

        print("\n### CASE:", label, "SENDER:", sender)

        try:
            pipe = original_pipeline(sender, msg)
        except Exception:
            pipe = {"error": traceback.format_exc()}

        try:
            whats = w.eldora_primary_runtime_reply(sender, msg)
        except Exception:
            whats = "ERROR:\n" + traceback.format_exc()

        results[msg][label] = {
            "pipeline_answer": pipe.get("answer") if isinstance(pipe, dict) else str(pipe),
            "pipeline_intent": pipe.get("intent") if isinstance(pipe, dict) else None,
            "whatsapp_answer": whats
        }

        print("PIPELINE_DIRECT:", str(results[msg][label]["pipeline_answer"])[:1000])
        print("WHATSAPP_FINAL :", str(whats)[:1000])

print("\n" + "=" * 100)
print("COMPACT_RESULTS")
print("=" * 100)
print(json.dumps(results, ensure_ascii=False, indent=2, default=str)[:20000])

print("\n" + "=" * 100)
print("OVERRIDE VERDICT")
print("=" * 100)

for msg, group in results.items():
    pipe_set = set(str(v["pipeline_answer"]) for v in group.values())
    whats_set = set(str(v["whatsapp_answer"]) for v in group.values())

    print("INPUT:", msg)
    print("PIPELINE_VARIANTS:", len(pipe_set))
    print("WHATSAPP_VARIANTS:", len(whats_set))

    if len(pipe_set) > 1 and len(whats_set) == 1:
        print("STATUS: WHATSAPP_COLLAPSES_MEMORY_VARIATION")
    elif len(pipe_set) > 1 and len(whats_set) > 1:
        print("STATUS: WHATSAPP_PRESERVES_VARIATION")
    else:
        print("STATUS: NO_PIPELINE_VARIATION_OR_NOT_APPLICABLE")

print("P4.63H_COMPLETE")
