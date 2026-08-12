from pathlib import Path

p = Path("app/api/whatsapp.py")
txt = p.read_text(encoding="utf-8")

anchor = "def eldora_primary_runtime_reply(sender_id: str, inbound_text: str):"

if "P19P26A_H4_ELDORA_IDENTITY_LOCK" not in txt:

    inject = '''
def eldora_primary_runtime_reply(sender_id: str, inbound_text: str):
    # P19P26A_H4_ELDORA_IDENTITY_LOCK
    _txt = str(inbound_text or "").lower()

    eldora_terms = [
        "eldora",
        "mind",
        "whatsapp",
        "lançar a eldora",
        "lancar a eldora",
        "lançamento eldora",
        "lancamento eldora"
    ]

    if any(t in _txt for t in eldora_terms):

        if "humanizada" in _txt or "humanizar" in _txt or "emoção" in _txt or "emocao" in _txt:
            return (
                "Hoje eu ainda respondo de forma muito técnica em alguns momentos. "
                "O próximo passo é fortalecer memória de longo prazo, continuidade de conversa, "
                "opinião contextual e reação emocional leve. A ideia é conversar como alguém que "
                "acompanha a jornada da pessoa, não como um manual."
            )

        if "lançar" in _txt or "lancar" in _txt:
            return (
                "Para lançar a Eldora no WhatsApp eu focaria primeiro em aquisição e retenção. "
                "A prioridade é gerar conversas reais, criar rotina de uso e transformar usuários "
                "em recorrentes antes de escalar mídia."
            )

    # /P19P26A_H4_ELDORA_IDENTITY_LOCK
'''

    txt = txt.replace(anchor, inject, 1)

p.write_text(txt, encoding="utf-8")
print("PATCH_OK")
