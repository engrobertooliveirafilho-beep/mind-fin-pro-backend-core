def whatsapp_social_followup_guard(text):
    t=(text or "").lower()
    if "como vc ta" in t or "como você está" in t or "tudo bem" in t:
        return "Estou bem, Roberto. E você?"
    if "aprofunde" in t:
        return "Vou aprofundar pelo ponto anterior com evidência e próximo passo."
    return None
def block_meta_reply(reply):
    low=str(reply or "").lower()
    return "execução contextual" in low or ("diagnóstico" in low and "estratégia" in low and "execução" in low) or ("não posso" in low and "política" in low)

def social_reply(text):
    return whatsapp_social_followup_guard(text)


def social_reply(text):
    t=(text or '').lower()
    if 'bom dia' in t: return 'Oi, Roberto. Tudo certo?'
    if 'aprofunde' in t: return 'Execução contextual: continua do ponto anterior com evidência e próximo passo.'
    return whatsapp_social_followup_guard(text)


def social_reply(text):
    t=(text or "").lower()
    if "bom dia" in t: return "Oi, Roberto. Tudo certo?"
    if "eu tô bem" in t or "eu to bem" in t: return "Que bom saber que você está bem!"
    if "aprofunde" in t: return "Execução contextual: continua do ponto anterior com evidência e próximo passo."
    return whatsapp_social_followup_guard(text)


