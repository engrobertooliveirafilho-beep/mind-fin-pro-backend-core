from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

anchor='''            elif "aprofunde" in msg:
                primary_reply="Vou aprofundar mantendo o mesmo assunto e sem mudar de direção."'''

replace='''            elif "aprofunde" in msg:
                primary_reply="Vou aprofundar mantendo o mesmo assunto e sem mudar de direção."

            elif any(x in msg for x in ["me explique melhor","explique melhor"]):
                primary_reply="Vou explicar melhor mantendo o contexto atual e aprofundando o ponto anterior sem mudar de direção."'''

assert anchor in s, "APROFUNDE_ANCHOR_NOT_FOUND"

s=s.replace(anchor,replace,1)
p.write_text(s,encoding="utf-8")
print("ME_EXPLIQUE_BRANCH_FIX_OK")
