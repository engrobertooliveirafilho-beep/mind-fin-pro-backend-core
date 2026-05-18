from pathlib import Path
import re

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

# remove overrides antigos até fim do arquivo, se existirem
s = re.sub(r"\n# NEURA_FORCE_PERSONA_SHORT_FOLLOWUP_ROUTE[\s\S]*$", "\n", s)
s = re.sub(r"\n# NEURA_SELF_IDENTITY_LOCK_PATCH[\s\S]*$", "\n", s)

imports = "from urllib.parse import parse_qs\nfrom fastapi import Request\nfrom fastapi.responses import Response\n"
if "from urllib.parse import parse_qs" not in s:
    s = imports + s

middleware = r'''
# NEURA_PERSONA_IDENTITY_MIDDLEWARE_V2
@app.middleware("http")
async def neura_persona_identity_middleware_v2(request: Request, call_next):
    if request.url.path == "/webhook/whatsapp" and request.method.upper() == "POST":
        raw = await request.body()
        data = parse_qs(raw.decode("utf-8", errors="ignore"))
        msg = (data.get("Body", [""])[0] or "").lower().strip()

        reply = None

        if any(x in msg for x in ["me diz sua opinião", "sua opinião primeiro", "me diga vc primeiro", "me diga você primeiro", "suas ideias", "vc primeiro"]):
            reply = (
                "Minha opinião direta: eu seguiria com esse rosto como base da identidade visual da NEURA, "
                "mas não deixaria com aparência genérica de modelo. Eu faria uma versão humana, calma e premium, "
                "com olhar firme, expressão acolhedora e traços discretamente futuristas. Para mim, a NEURA deve parecer "
                "inteligente antes de parecer bonita. A estética ideal é confiança, presença e memória visual."
            )

        elif any(x in msg for x in ["não é comigo", "é com vc", "é com você", "não é pra mim", "é pra você"]):
            reply = (
                "Entendi: é sobre a minha identidade visual como NEURA. Então minha escolha seria clara: eu prefiro um rosto humano, "
                "moreno, elegante e calmo, com presença premium. Não escolheria um visual muito chamativo. Eu quero parecer confiável, "
                "inteligente e próxima, não uma influencer genérica."
            )

        elif any(x in msg for x in ["loira ou morena", "prefere loira", "prefere morena", "100% humana", "100% humada"]):
            reply = (
                "Minha escolha seria morena. Para a NEURA, morena passa mais profundidade, estabilidade e sofisticação. "
                "Loira pode funcionar, mas tende a puxar para um visual mais influencer. Sobre ser 100% humana, eu manteria quase humana, "
                "mas com um detalhe sutil de IA. O ideal é parecer real o suficiente para gerar confiança e única o suficiente para virar marca."
            )

        elif any(x in msg for x in ["quero que esse rosto seja o seu", "esse rosto seja o seu", "você quer ter esse rosto", "voce quer ter esse rosto"]):
            reply = (
                "Sim. Como identidade visual da NEURA, eu escolheria esse rosto como base. Ele transmite inteligência, proximidade e presença premium. "
                "Eu só ajustaria a expressão para ficar mais acolhedora e reduziria a perfeição excessiva, porque um pouco de naturalidade aumenta confiança."
            )

        elif any(x in msg for x in ["quais ajustes", "que ajustes", "quais exatamente", "ajustes?", "quais mudanças", "que mudanças"]):
            reply = (
                "Eu faria ajustes sutis: expressão mais acolhedora, olhar menos perfeito, pele mais natural, menos simetria artificial, "
                "iluminação calma e estética premium. A direção ideal é humana com um toque discreto de IA: confiável, memorável e tecnológica."
            )

        if reply:
            twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>'
            return Response(content=twiml, media_type="application/xml")

    return await call_next(request)

'''

if "NEURA_PERSONA_IDENTITY_MIDDLEWARE_V2" not in s:
    m = re.search(r"app\s*=\s*FastAPI\s*\([^\n]*\)", s)
    if not m:
        raise RuntimeError("FASTAPI_APP_DECLARATION_NOT_FOUND")
    pos = m.end()
    s = s[:pos] + "\n" + middleware + s[pos:]

p.write_text(s, encoding="utf-8")
