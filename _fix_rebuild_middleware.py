from pathlib import Path
import re

p = Path("app/main.py")
txt = p.read_text(encoding="utf-8")

# ====================================================
# REBUILD middleware quebrado
# ====================================================

pattern = r'@app\.middleware\("http"\)\s*async def neura_persona_identity_middleware_v2\(.*?return await call_next\(request\)'
replacement = '''@app.middleware("http")
async def neura_persona_identity_middleware_v2(request: Request, call_next):
    event("MAIN_INTERCEPTOR_CHECK", route="/webhook/whatsapp", module_name="app.main")

    msg = ""
    reply = None

    if request.url.path == "/webhook/whatsapp" and request.method.upper() == "POST":
        raw = await request.body()
        data = parse_qs(raw.decode("utf-8", errors="ignore"))
        msg = (data.get("Body", [""])[0] or "").lower().strip()

        if any(x in msg for x in [
            "me diz sua opinião","sua opinião primeiro",
            "me diga vc primeiro","me diga você primeiro",
            "suas ideias","vc primeiro"
        ]):
            reply = (
                "Minha opinião direta: eu seguiria com esse rosto como base da identidade visual da NEURA, "
                "mas não deixaria com aparência genérica de modelo. Eu faria uma versão humana, calma e premium, "
                "com olhar firme, expressão acolhedora e traços discretamente futuristas. Para mim, a NEURA deve parecer "
                "inteligente antes de parecer bonita. A estética ideal é confiança, presença e memória visual."
            )

        elif any(x in msg for x in [
            "não é comigo","é com vc","é com você",
            "não é pra mim","é pra você"
        ]):
            reply = (
                "Entendi: é sobre a minha identidade visual como NEURA. Então minha escolha seria clara: "
                "eu prefiro um rosto humano, moreno, elegante e calmo, com presença premium."
            )

        elif any(x in msg for x in [
            "loira ou morena","prefere loira",
            "prefere morena","100% humana","100% humada"
        ]):
            reply = (
                "Minha escolha seria morena. Para a NEURA, morena passa profundidade, estabilidade e sofisticação."
            )

        elif any(x in msg for x in [
            "quero que esse rosto seja o seu",
            "esse rosto seja o seu",
            "você quer ter esse rosto",
            "voce quer ter esse rosto"
        ]):
            reply = (
                "Sim. Como identidade visual da NEURA, eu escolheria esse rosto como base."
            )

        elif any(x in msg for x in [
            "quais ajustes","que ajustes",
            "quais exatamente","ajustes?",
            "quais mudanças","que mudanças"
        ]):
            reply = (
                "Eu faria ajustes sutis: expressão mais acolhedora, pele mais natural, "
                "menos perfeição artificial e iluminação premium."
            )

        if reply:
            twiml = (
                '<?xml version="1.0" encoding="UTF-8"?>'
                f'<Response><Message>{sanitize_final_human_output(reply)}</Message></Response>'
            )
            event("MAIN_INTERCEPTOR_RETURN",
                  route="/webhook/whatsapp",
                  module_name="app.main")
            return Response(content=twiml, media_type="application/xml")

    return await call_next(request)'''

txt = re.sub(pattern, replacement, txt, flags=re.S)

# remove lixo residual FIX11K
txt = re.sub(r'.*_fix11k_trace.*\n?', '', txt)
txt = re.sub(r'.*save\(_fix11k_trace\).*\n?', '', txt)
txt = re.sub(r'.*mark\(_fix11k_trace.*\n?', '', txt)

p.write_text(txt, encoding="utf-8")

print("NEURA_MIDDLEWARE_REBUILT_OK")
