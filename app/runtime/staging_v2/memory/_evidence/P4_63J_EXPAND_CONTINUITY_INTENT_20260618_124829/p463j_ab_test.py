from app.runtime.short_memory import remember, recall
from app.api.whatsapp import eldora_primary_runtime_reply

cases = {
    "A_CONFINAMENTO": {
        "sender": "p463j_A_confinamento",
        "memory": "ASSUNTO_ATIVO=confinamento de boi; foco=água, cocho, balança, trato, sensores, alertas"
    },
    "B_ELDORA": {
        "sender": "p463j_B_eldora",
        "memory": "ASSUNTO_ATIVO=lançamento Eldora; foco=persona, WhatsApp, aquisição, retenção, canary"
    },
    "C_DEBUG": {
        "sender": "p463j_C_debug",
        "memory": "ASSUNTO_ATIVO=debug runtime; foco=traceback, pytest, app/main.py, cognitive_pipeline, evidência"
    }
}

for label, cfg in cases.items():
    remember("active_context", cfg["memory"], sender_id=cfg["sender"])
    print(label, "MEMORY:", recall("active_context", sender_id=cfg["sender"]))

inputs = [
    "e depois?",
    "prossiga",
    "qual próximo passo?",
    "próximo passo",
    "e agora?",
    "como continuar?"
]

print("\n===== WHATSAPP A/B AFTER P4.63J =====")

all_ok = True

for msg in inputs:
    print("\n" + "=" * 90)
    print("INPUT:", msg)
    answers = []

    for label, cfg in cases.items():
        out = eldora_primary_runtime_reply(cfg["sender"], msg)
        answers.append(str(out))
        print("\nCASE:", label)
        print(str(out)[:1500])

    variants = len(set(answers))
    print("\nVARIANTS:", variants)

    if variants > 1:
        print("STATUS: MEMORY_VARIATION_PRESERVED")
    else:
        print("STATUS: STILL_COLLAPSED")
        all_ok = False

print("\nP4.63J_ALL_CONTINUITY_MEMORY_VARIATION:", all_ok)
print("P4.63J_AB_TEST_COMPLETE")
