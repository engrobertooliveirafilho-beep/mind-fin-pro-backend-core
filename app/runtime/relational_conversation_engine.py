from app.runtime.subject_alias_engine import subject_alias
import re

def relationalize(message:str, text:str, ctx:dict|None=None)->str:
    ctx=ctx or {}

    subject=ctx.get("last_subject","")
    alias=subject_alias(subject)

    out=str(text or "").strip()

    out=out.replace(subject, alias)

    replacements = {
        "eu olharia":"se fosse eu, eu olharia",
        "vale a pena sim":"eu teria coragem, mas",
        "melhor fugir":"eu passaria",
        "moto maquiada vira gasto rápido":"às vezes parece boa no começo e depois começa a aparecer coisa escondida"
    }

    for a,b in replacements.items():
        out=out.replace(a,b)

    out=re.sub(r'\s+',' ',out).strip()

    return out
