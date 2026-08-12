from app.runtime.short_memory import remember, recall
from app.api.whatsapp import eldora_primary_runtime_reply

cases = {
    "A_CONFINAMENTO": {
        "sender": "p463m_after_A",
        "memory": "ASSUNTO_ATIVO=confinamento de boi; foco=água, cocho, balança, trato, sensores, alertas"
    },
    "B_ELDORA": {
        "sender": "p463m_after_B",
        "memory": "ASSUNTO_ATIVO=lançamento Eldora; foco=persona, WhatsApp, aquisição, retenção, canary"
    },
    "C_DEBUG": {
        "sender": "p463m_after_C",
        "memory": "ASSUNTO_ATIVO=debug runtime; foco=traceback, pytest, app/main.py, cognitive_pipeline, evidência"
    }
}

inputs = ["e depois?", "prossiga", "qual próximo passo?", "e agora?", "como continuar?", "quero automatizar confinamento de boi"]

print("P4.63M SNAPSHOT AFTER")
for label, cfg in cases.items():
    remember("active_context", cfg["memory"], sender_id=cfg["sender"])
    print(label, "MEMORY=", recall("active_context", sender_id=cfg["sender"]))

all_ok = True

for msg in inputs:
    print("\nINPUT:", msg)
    answers = []
    for label, cfg in cases.items():
        out = str(eldora_primary_runtime_reply(cfg["sender"], msg))
        answers.append(out)
        print(label, "=>", out[:800])

    variants = len(set(answers))
    print("VARIANTS:", variants)

    if msg != "quero automatizar confinamento de boi" and variants <= 1:
        all_ok = False
        print("LOCK: FAIL")
    else:
        print("LOCK: PASS")

print("P4.63M_AFTER_LOCK:", all_ok)
