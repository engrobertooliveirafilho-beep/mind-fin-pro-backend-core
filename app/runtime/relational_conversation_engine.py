from app.runtime.subject_alias_engine import subject_alias
import re

def relationalize(message:str, text:str, ctx:dict|None=None)->str:
    ctx=ctx or {}
    subject=ctx.get("last_subject","")
    alias=subject_alias(subject)
    out=str(text or "").strip()

    if subject and alias:
        out=out.replace(subject, alias)

    fixes={
        "a essa moto":"essa moto",
        "na essa moto":"nessa moto",
        "da essa moto":"dessa moto",
        "do essa moto":"dessa moto",
        "essa moto pode":"essa moto pode",
        "se fosse eu, eu olharia":"se fosse eu, olharia",
    }
    for a,b in fixes.items():
        out=out.replace(a,b)

    replacements={
        "eu olharia":"se fosse eu, olharia",
        "Vale a pena sim":"Eu teria coragem",
        "vale a pena sim":"eu teria coragem",
        "melhor fugir":"eu passaria",
        "moto maquiada vira gasto rápido":"às vezes parece boa no começo e depois começa a aparecer coisa escondida"
    }
    for a,b in replacements.items():
        out=out.replace(a,b)

    out=re.sub(r'\s+',' ',out).strip()
    return out
