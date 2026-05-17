from pathlib import Path
import re

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

if "neura_persona_short_followup_middleware" not in s:
    block = r'''
from urllib.parse import parse_qs
from fastapi import Request
from fastapi.responses import Response

@app.middleware("http")
async def neura_persona_short_followup_middleware(request: Request, call_next):
    if request.url.path == "/webhook/whatsapp" and request.method.upper() == "POST":
        body = (await request.body()).decode("utf-8", errors="ignore")
        fields = parse_qs(body)
        message = (fields.get("Body", [""])[0] or "").lower().strip()
        triggers = ["quais ajustes", "que ajustes", "quais exatamente", "ajustes?", "quais mudanças", "que mudanças"]
        if any(t in message for t in triggers):
            reply = (
                "Eu faria ajustes sutis, não mudaria a identidade principal do rosto. "
                "Suavizaria a expressão para parecer mais acolhedora, deixaria o olhar menos perfeito e mais humano, "
                "reduziria excesso de simetria para não parecer artificial, manteria a estética premium e usaria iluminação mais calma. "
                "A direção ideal para a NEURA é 70% humana e 30% futurista: confiável, memorável e sem assustar."
            )
            twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>'
            return Response(content=twiml, media_type="application/xml")
    return await call_next(request)

'''
    s = re.sub(r"(app\s*=\s*FastAPI\s*\([^\n]*\)\s*)", r"\1\n" + block, s, count=1)

p.write_text(s, encoding="utf-8")
