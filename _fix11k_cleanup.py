from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

# remover bloco rescue duplicado (segunda ocorrência antiga)
dup='''            msg=(message or "").lower().strip()
            bad_reply=(not primary_reply) or str(primary_reply).strip().lower() in ["entendi. continua.","entendi.\n\ncontinua."]
            if any(x in msg for x in ["quem é você","quem é vc","quem e vc","quem e você","quem é voce","quem e voce"]) and (bad_reply or "tudo certo" in str(primary_reply).lower()):
                primary_reply="Sou a Eldora 🙂 O que você quer saber?"
            elif any(x in msg for x in ["como você está","como vc está","vc está bem","tudo bem"]) and bad_reply:
                primary_reply="Tudo certo por aqui 🙂 E você?"
            elif ("quanto é" in msg or "x" in msg) and bad_reply:
                primary_reply=safe_reply(message)
            elif any(x in msg for x in ["e depois","depois?"]) and bad_reply:
                primary_reply="Depois mantemos contexto, validamos o fluxo real e seguimos sem reset semântico."
'''

if s.count(dup) >= 1:
    s=s.replace(dup,"",1)

# me explique melhor
anchor='''            elif any(x in msg for x in ["deu errado","como resolvemos","busque pelo problema","procure o erro principal","consegue detalhar"]):
                primary_reply="Vamos localizar a causa raiz, validar o hop problemático e corrigir sem quebrar o restante do pipeline."'''

replace=anchor+'''
            elif any(x in msg for x in ["me explique melhor","explique melhor"]):
                primary_reply="Vou explicar melhor mantendo o contexto atual, aprofundando sem resetar a conversa."'''

assert anchor in s, "ANCHOR_NOT_FOUND"

s=s.replace(anchor,replace,1)

p.write_text(s,encoding="utf-8")
print("FIX11K_CLEANUP_OK")
