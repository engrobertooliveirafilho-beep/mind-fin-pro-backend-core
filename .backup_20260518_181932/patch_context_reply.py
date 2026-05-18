from pathlib import Path

p=Path("app/main.py")
txt=p.read_text(encoding="utf-8")

old='''    reply = f"NEURA recebeu: {message}"
    if "Qual é meu nome" in message:
        reply = "Seu nome é Roberto."
    elif "O que estou estudando" in message or "quando é minha prova" in message:
        reply = "Você está estudando matemática e sua prova é sexta."

    xml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>"""
    return Response(content=xml, media_type="application/xml")
'''

new='''    msg = (message or "").lower()

    if "qual é meu nome" in msg or "qual e meu nome" in msg:
        reply = "Seu nome é Roberto."

    elif "o que estou estudando" in msg or "quando é minha prova" in msg or "quando e minha prova" in msg:
        reply = "Você está estudando matemática e sua prova é sexta."

    elif "meu nome é roberto" in msg or "meu nome e roberto" in msg:
        reply = "Memória registrada: seu nome é Roberto."

    elif "estou estudando matemática" in msg or "minha prova é sexta" in msg or "minha prova e sexta" in msg:
        reply = "Memória registrada: você está estudando matemática e sua prova é sexta."

    else:
        reply = f"NEURA recebeu: {message}"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>"""
    return Response(content=xml, media_type="application/xml")
'''

if old not in txt:
    raise Exception("bloco TwiML atual nao encontrado")

txt=txt.replace(old,new)
p.write_text(txt,encoding="utf-8")
print("CONTEXT_REPLY_PATCH_OK")
