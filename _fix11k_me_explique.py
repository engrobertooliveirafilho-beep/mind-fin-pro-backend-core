from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

old='''            elif any(x in msg for x in ["me explique melhor","explique melhor"]):
                primary_reply="Vou explicar melhor mantendo o contexto atual, aprofundando sem resetar a conversa."'''

new='''            elif any(x in msg for x in ["me explique melhor","explique melhor"]):
                primary_reply="Vou explicar melhor mantendo o contexto atual e aprofundar o ponto anterior sem mudar de direção."'''

if old not in s:
    anchor='''            elif any(x in msg for x in ["deu errado","como resolvemos","busque pelo problema","procure o erro principal","consegue detalhar"]):
                primary_reply="Vamos localizar a causa raiz, validar o hop problemático e corrigir sem quebrar o restante do pipeline."'''
    assert anchor in s, "ANCHOR_NOT_FOUND"
    s=s.replace(anchor,anchor+'''
            elif any(x in msg for x in ["me explique melhor","explique melhor"]):
                primary_reply="Vou explicar melhor mantendo o contexto atual e aprofundar o ponto anterior sem mudar de direção."''',1)
else:
    s=s.replace(old,new,1)

p.write_text(s,encoding="utf-8")
print("ME_EXPLIQUE_FIX_OK")
