from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

needle='''            if any(x in msg for x in ["quem é você","quem é vc","quem e vc","quem e você","quem é voce","quem e voce"]) and (bad_reply or "tudo certo" in str(primary_reply).lower()):'''

insert='''            if any(x in msg for x in ["me explique melhor","explique melhor"]):
                primary_reply="Vou explicar melhor mantendo o contexto atual e aprofundando o ponto anterior sem mudar de direção."
            elif any(x in msg for x in ["quem é você","quem é vc","quem e vc","quem e você","quem é voce","quem e voce"]) and (bad_reply or "tudo certo" in str(primary_reply).lower()):'''

assert needle in s, "ANCHOR_NOT_FOUND"
s=s.replace(needle,insert,1)

# remove duplicatas antigas
old='''            elif any(x in msg for x in ["me explique melhor","explique melhor"]):
                primary_reply="Vou explicar melhor mantendo o contexto atual, aprofundando sem resetar a conversa."
'''
s=s.replace(old,"")

old2='''            elif any(x in msg for x in ["me explique melhor","explique melhor"]):
                primary_reply="Vou explicar melhor mantendo o contexto atual e aprofundar o ponto anterior sem mudar de direção."
'''
s=s.replace(old2,"")

p.write_text(s,encoding="utf-8")
print("ME_EXPLIQUE_PRIORITY_FIX_OK")
