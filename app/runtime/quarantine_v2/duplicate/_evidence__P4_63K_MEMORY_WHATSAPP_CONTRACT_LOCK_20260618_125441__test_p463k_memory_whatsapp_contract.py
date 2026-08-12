from app.runtime.short_memory import remember, recall
from app.api.whatsapp import eldora_primary_runtime_reply


def test_p463k_memory_variation_preserved_for_continuity_followups():
    cases = {
        "A_CONFINAMENTO": {
            "sender": "p463k_A_confinamento",
            "memory": "ASSUNTO_ATIVO=confinamento de boi; foco=água, cocho, balança, trato, sensores, alertas",
        },
        "B_ELDORA": {
            "sender": "p463k_B_eldora",
            "memory": "ASSUNTO_ATIVO=lançamento Eldora; foco=persona, WhatsApp, aquisição, retenção, canary",
        },
        "C_DEBUG": {
            "sender": "p463k_C_debug",
            "memory": "ASSUNTO_ATIVO=debug runtime; foco=traceback, pytest, app/main.py, cognitive_pipeline, evidência",
        },
    }

    for cfg in cases.values():
        remember("active_context", cfg["memory"], sender_id=cfg["sender"])
        assert recall("active_context", sender_id=cfg["sender"])

    followups = [
        "e depois?",
        "prossiga",
        "qual próximo passo?",
        "próximo passo",
        "e agora?",
        "como continuar?",
    ]

    for msg in followups:
        answers = [
            str(eldora_primary_runtime_reply(cfg["sender"], msg))
            for cfg in cases.values()
        ]

        assert len(set(answers)) > 1, (
            "WhatsApp collapsed memory variation for continuity followup: "
            f"{msg} -> {answers}"
        )


def test_p463k_whatsapp_does_not_break_direct_domain_answer():
    sender = "p463k_domain_confinamento"

    remember(
        "active_context",
        "ASSUNTO_ATIVO=confinamento de boi; foco=trato, água, balança, cocho e alertas",
        sender_id=sender,
    )

    out = str(eldora_primary_runtime_reply(sender, "quero automatizar confinamento de boi")).lower()

    assert "confinamento" in out
    assert "trato" in out or "cocho" in out or "balança" in out or "balanca" in out
