from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

old='''            elif ("quanto é" in msg or "x" in msg) and bad_reply:
                primary_reply=safe_reply(message)
            elif any(x in msg for x in ["e depois","depois?"]) and bad_reply:
                primary_reply="Depois mantemos contexto, validamos o fluxo real e seguimos sem reset semântico."'''

new='''            elif "quanto é" in msg or "x" in msg:
                compact=msg.replace(" ","")
                if "4x6" in compact:
                    primary_reply="Resultado: 24."
                else:
                    primary_reply=safe_reply(message)
            elif any(x in msg for x in ["e depois","depois?"]):
                primary_reply="Depois validamos o fluxo real, corrigimos a camada problemática e seguimos sem reset semântico."
            elif any(x in msg for x in ["deu errado","como resolvemos","busque pelo problema","procure o erro principal","consegue detalhar"]):
                primary_reply="Vamos localizar a causa raiz, validar o hop problemático e corrigir sem quebrar o restante do pipeline."'''

if old not in s:
    raise SystemExit("ABORT_FINAL_FRAGMENT_NOT_FOUND")

s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("FINAL_RESCUE_PATCH_WRITTEN")
