import json
import difflib
import traceback

from app.runtime.cognitive_pipeline import run_cognitive_pipeline
from app.api.whatsapp import eldora_primary_runtime_reply
from app.runtime.short_memory import remember, recall

def dump(label, obj):
    print("\n" + "=" * 90)
    print(label)
    print("=" * 90)
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str)[:8000])

def safe_pipeline(sender, msg):
    try:
        return run_cognitive_pipeline(sender, msg)
    except Exception:
        return {"error": traceback.format_exc()}

def safe_whatsapp(sender, msg):
    try:
        return eldora_primary_runtime_reply(sender, msg)
    except Exception:
        return "ERROR:\n" + traceback.format_exc()

def compact(result):
    if not isinstance(result, dict):
        return {"raw": str(result)}
    return {
        "answer": result.get("answer"),
        "intent": result.get("intent"),
        "scores": result.get("scores"),
        "state": result.get("state"),
        "social": result.get("social"),
        "emotion": result.get("emotion"),
        "relationship": result.get("relationship"),
    }

def diff_text(a, b):
    a = str(a or "").splitlines()
    b = str(b or "").splitlines()
    return "\n".join(difflib.unified_diff(a, b, fromfile="A", tofile="B", lineterm=""))

sender_a = "p463g_memory_A_confinamento"
sender_b = "p463g_memory_B_eldora"
sender_c = "p463g_memory_C_debug"

print("P4.63G_START")

# Memórias distintas para o MESMO input ambíguo
remember("active_context", "ASSUNTO_ATIVO=confinamento de boi; foco=água, cocho, balança, trato, sensores, alertas", sender_id=sender_a)
remember("active_context", "ASSUNTO_ATIVO=lançamento Eldora; foco=persona, WhatsApp, aquisição, retenção, canary", sender_id=sender_b)
remember("active_context", "ASSUNTO_ATIVO=debug runtime; foco=traceback, pytest, app/main.py, cognitive_pipeline, evidência", sender_id=sender_c)

print("\n===== RAW RECALL =====")
for s in [sender_a, sender_b, sender_c]:
    try:
        print(s, "=>", recall("active_context", sender_id=s))
    except Exception:
        print(s, "RECALL_ERROR", traceback.format_exc())

ambiguous_inputs = [
    "e depois?",
    "como fazer?",
    "prossiga",
    "qual próximo passo?",
]

results = {}

for msg in ambiguous_inputs:
    results[msg] = {}

    for label, sender in [
        ("A_CONFINAMENTO", sender_a),
        ("B_ELDORA", sender_b),
        ("C_DEBUG", sender_c),
    ]:
        pipe = safe_pipeline(sender, msg)
        whats = safe_whatsapp(sender, msg)

        results[msg][label] = {
            "pipeline": compact(pipe),
            "whatsapp": whats,
        }

dump("FULL_RESULTS", results)

print("\n" + "=" * 90)
print("A/B/C ANSWER COMPARISON")
print("=" * 90)

for msg, group in results.items():
    print("\nINPUT:", msg)

    a = group["A_CONFINAMENTO"]["pipeline"]["answer"]
    b = group["B_ELDORA"]["pipeline"]["answer"]
    c = group["C_DEBUG"]["pipeline"]["answer"]

    print("\nPIPELINE_A:", a)
    print("PIPELINE_B:", b)
    print("PIPELINE_C:", c)

    print("\nDIFF A vs B:")
    print(diff_text(a, b)[:3000])

    print("\nDIFF A vs C:")
    print(diff_text(a, c)[:3000])

    wa = group["A_CONFINAMENTO"]["whatsapp"]
    wb = group["B_ELDORA"]["whatsapp"]
    wc = group["C_DEBUG"]["whatsapp"]

    print("\nWHATSAPP_A:", wa)
    print("WHATSAPP_B:", wb)
    print("WHATSAPP_C:", wc)

    print("\nWHATSAPP DIFF A vs B:")
    print(diff_text(wa, wb)[:3000])

print("\n" + "=" * 90)
print("P4.63G VERDICT")
print("=" * 90)

influence_detected = False

for msg, group in results.items():
    answers = [
        str(group["A_CONFINAMENTO"]["pipeline"]["answer"]),
        str(group["B_ELDORA"]["pipeline"]["answer"]),
        str(group["C_DEBUG"]["pipeline"]["answer"]),
    ]
    if len(set(answers)) > 1:
        influence_detected = True

print("MEMORY_INFLUENCE_DETECTED_ON_PIPELINE:", influence_detected)

whatsapp_influence_detected = False

for msg, group in results.items():
    answers = [
        str(group["A_CONFINAMENTO"]["whatsapp"]),
        str(group["B_ELDORA"]["whatsapp"]),
        str(group["C_DEBUG"]["whatsapp"]),
    ]
    if len(set(answers)) > 1:
        whatsapp_influence_detected = True

print("MEMORY_INFLUENCE_DETECTED_ON_WHATSAPP:", whatsapp_influence_detected)

print("P4.63G_COMPLETE")
