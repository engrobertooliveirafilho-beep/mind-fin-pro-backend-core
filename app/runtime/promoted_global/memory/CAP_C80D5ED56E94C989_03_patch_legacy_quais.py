from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

s = s.replace(
'''    if msg in short_followups:
        intent = _P19P27B_LAST_INTENT.get(sender, "")
''',
'''    if msg in short_followups:
        if _p19p30d_has_universal_context(sender):
            return out
        intent = _P19P27B_LAST_INTENT.get(sender, "")
'''
)

s = s.replace(
'''    if msg.strip() in ["quais são", "quais sao", "quais?", "quais são?", "quais sao?"]:
        return wrap("São estes: memória real, continuidade, resposta menos engessada, opinião contextual, emoção leve e zero reset do assunto.")
''',
'''    if msg.strip() in ["quais são", "quais sao", "quais?", "quais são?", "quais sao?"]:
        if _p19p30d_has_universal_context(sender if "sender" in locals() else "unknown"):
            return out
        return wrap("São estes: memória real, continuidade, resposta menos engessada, opinião contextual, emoção leve e zero reset do assunto.")
'''
)

s = s.replace(
'''    if msg.strip() in ["quais são", "quais sao", "quais?", "quais são?", "quais sao?"]:
        return "São estes: memória real, continuidade, resposta menos engessada, opinião contextual, emoção leve e zero reset do assunto."
''',
'''    if msg.strip() in ["quais são", "quais sao", "quais?", "quais são?", "quais sao?"]:
        if _p19p30d_has_universal_context(locals().get("sender_id", "unknown")):
            return txt
        return "São estes: memória real, continuidade, resposta menos engessada, opinião contextual, emoção leve e zero reset do assunto."
'''
)

s = s.replace(
'''    if msg.strip() in ["quais são", "quais sao", "quais?", "quais são?", "quais sao?"]:
        return (
            "São estes: memória real do contexto, frases mais naturais, menos lista engessada, "
            "opinião contextual, reação emocional leve e continuidade sem resetar o assunto."
        )
''',
'''    if msg.strip() in ["quais são", "quais sao", "quais?", "quais são?", "quais sao?"]:
        if _p19p30d_has_universal_context(locals().get("sender_id", "unknown")):
            return txt
        return (
            "São estes: memória real do contexto, frases mais naturais, menos lista engessada, "
            "opinião contextual, reação emocional leve e continuidade sem resetar o assunto."
        )
'''
)

p.write_text(s, encoding="utf-8")
print("P19P30D_LEGACY_QUAIS_GUARDS_OK")
