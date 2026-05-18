from pathlib import Path

p=Path("app/main.py")
txt=p.read_text(encoding="utf-8")

txt = txt.replace(
'from fastapi import Request',
'from fastapi import Request, Response'
)

old='''    return {
        "status":"ok",
        "sender_id":sender_id,
        "message":message,
        "payload":payload
    }
'''

new='''    reply = f"NEURA recebeu: {message}"
    if "Qual é meu nome" in message:
        reply = "Seu nome é Roberto."
    elif "O que estou estudando" in message or "quando é minha prova" in message:
        reply = "Você está estudando matemática e sua prova é sexta."

    xml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>"""
    return Response(content=xml, media_type="application/xml")
'''

if old not in txt:
    raise Exception("bloco return JSON nao encontrado")

txt=txt.replace(old,new)
p.write_text(txt,encoding="utf-8")
print("TWILIO_XML_PATCH_OK")
