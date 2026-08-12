from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

old = '''        expanded_message = (
            "Continue a conversa anterior usando o contexto recuperado. "
            "Não responda apenas confirmação. Entregue a continuação útil do assunto. "
            f"Contexto: {state_context}\\n"
            f"Pedido atual: {inbound_text}"
        )

        visible = run_cognitive_pipeline(sender_id, expanded_message)
'''

new = '''        # P4.63I - Preserve memory-specific context in WhatsApp continuity.
        # The previous generic wrapper collapsed memory variation into a fixed MIND continuation.
        active_context = ""
        try:
            from app.runtime.short_memory import recall as _p463i_recall
            active_context = str(_p463i_recall("active_context", sender_id=sender_id) or "")
        except Exception:
            active_context = ""

        if active_context.strip():
            expanded_message = (
                "CONTEXTO_ATIVO_MEMORIA: " + active_context + "\\n"
                "PEDIDO_ATUAL: " + str(inbound_text or "") + "\\n"
                "Responda continuando exatamente o assunto do CONTEXTO_ATIVO_MEMORIA. "
                "Não substitua por status genérico do MIND. "
                "Não reinicie a conversa."
            )
        else:
            expanded_message = (
                "Continue a conversa anterior usando o contexto recuperado. "
                "Não responda apenas confirmação. Entregue a continuação útil do assunto. "
                f"Contexto: {state_context}\\n"
                f"Pedido atual: {inbound_text}"
            )

        visible = run_cognitive_pipeline(sender_id, expanded_message)
'''

if old not in s:
    raise SystemExit("PATCH_TARGET_NOT_FOUND")

s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("PATCH_APPLIED_OK")
