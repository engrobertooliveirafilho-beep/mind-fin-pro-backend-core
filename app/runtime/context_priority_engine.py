def context_priority_reply(message: str, sender_id: str = "default") -> str:
    msg = str(message or "").strip().lower()

    if msg in {"eldora", "eldora?", "vc é eldora?", "você é eldora?"}:
        return "Estou aqui 🙂 Pode mandar."

    if any(x in msg for x in ["integrações", "integracoes", "implantações", "implantacoes", "que fizemos", "o que fizemos"]):
        return "Sim. Fizemos Render live, WhatsApp webhook, Supabase/memória, multi-provider com 14 IAs, UX guard, canary health e ledger de evidências."

    if any(x in msg for x in ["deu certo", "agora deu certo", "funcionou", "conseguiu ver"]):
        return "Sim. A parte técnica subiu: multi-provider, WhatsApp, UX guard e canary. Falta fechar memória contextual/persona antes do P4.14."

    return ""
