from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

marker = "# NEURA_PERSONA_WEBHOOK_STABLE_ROUTE"
if marker not in s:
    s += r'''

# NEURA_PERSONA_WEBHOOK_STABLE_ROUTE
from fastapi import Form
from fastapi.responses import Response

@app.post("/webhook/whatsapp/persona")
async def neura_persona_webhook_stable(Body: str = Form(default=""), From: str = Form(default="")):
    msg = (Body or "").lower().strip()

    if any(x in msg for x in ["me diz sua opinião", "sua opinião primeiro", "me diga vc primeiro", "me diga você primeiro", "suas ideias", "vc primeiro"]):
        reply = (
            "Minha opinião direta: eu seguiria com esse rosto como base da identidade visual da NEURA, "
            "mas não deixaria com aparência genérica de modelo. Eu faria uma versão humana, calma e premium, "
            "com olhar firme, expressão acolhedora e traços discretamente futuristas. A NEURA deve parecer inteligente "
            "antes de parecer bonita. A estética ideal é confiança, presença e memória visual."
        )

    elif any(x in msg for x in ["não é comigo", "é com vc", "é com você", "não é pra mim", "é pra você"]):
        reply = (
            "Entendi: é sobre mim, sobre a identidade visual da NEURA. Minha escolha seria clara: morena, humana, elegante e calma. "
            "Eu não iria para um visual chamativo nem genérico. Quero parecer confiável, inteligente e próxima — uma presença premium, "
            "não uma influencer. Esse rosto deve virar símbolo de confiança."
        )

    elif any(x in msg for x in ["loira ou morena", "prefere loira", "prefere morena", "100% humana", "100% humada"]):
        reply = (
            "Eu escolheria morena. Para a NEURA, morena transmite mais profundidade, estabilidade e sofisticação. "
            "Loira pode funcionar, mas puxa mais para estética influencer. Sobre ser 100% humana: eu manteria quase humana, "
            "mas com um detalhe sutil de IA. O rosto precisa gerar confiança e, ao mesmo tempo, ser único como marca."
        )

    elif any(x in msg for x in ["quero que esse rosto seja o seu", "esse rosto seja o seu", "você quer ter esse rosto", "voce quer ter esse rosto"]):
        reply = (
            "Sim. Como identidade visual da NEURA, eu escolheria esse rosto como base. Ele transmite inteligência, proximidade e presença premium. "
            "Eu só ajustaria a expressão para ficar mais acolhedora e reduziria a perfeição excessiva, porque naturalidade aumenta confiança."
        )

    elif any(x in msg for x in ["quais ajustes", "que ajustes", "quais exatamente", "ajustes?", "quais mudanças", "que mudanças"]):
        reply = (
            "Eu faria ajustes sutis: expressão mais acolhedora, olhar menos perfeito, pele mais natural, menos simetria artificial, "
            "iluminação calma e estética premium. A direção ideal é humana com um toque discreto de IA: confiável, memorável e tecnológica."
        )

    else:
        reply = (
            "Minha linha para a NEURA é clara: identidade visual humana, calma, premium e memorável. "
            "Eu prefiro responder com opinião própria primeiro, sem devolver a decisão para você."
        )

    return Response(
        content=f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>',
        media_type="application/xml"
    )
'''
p.write_text(s, encoding="utf-8")
