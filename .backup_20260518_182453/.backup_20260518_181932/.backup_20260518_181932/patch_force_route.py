from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

marker = "# NEURA_FORCE_PERSONA_SHORT_FOLLOWUP_ROUTE"
if marker not in s:
    append = r'''

# NEURA_FORCE_PERSONA_SHORT_FOLLOWUP_ROUTE
from fastapi import Form
from fastapi.responses import Response

@app.post("/webhook/whatsapp")
async def neura_forced_persona_webhook_override(Body: str = Form(default=""), From: str = Form(default="")):
    m = (Body or "").lower().strip()
    triggers = ["quais ajustes", "que ajustes", "quais exatamente", "ajustes?", "quais mudanças", "que mudanças"]

    if any(t in m for t in triggers):
        reply = (
            "Eu faria ajustes bem específicos: suavizar a expressão para parecer mais acolhedora, "
            "deixar o olhar menos perfeito e mais humano, reduzir excesso de simetria para não parecer artificial, "
            "manter a estética premium, usar iluminação mais calma e preservar a identidade principal do rosto. "
            "Para a NEURA, o ideal é 70% humana e 30% futurista: confiável, memorável e tecnológica sem assustar."
        )
        return Response(
            content=f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>',
            media_type="application/xml"
        )

    reply = "Mensagem recebida. Para ajustes da persona visual, envie: quais ajustes?"
    return Response(
        content=f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>',
        media_type="application/xml"
    )
'''
    s = s + append

p.write_text(s, encoding="utf-8")
