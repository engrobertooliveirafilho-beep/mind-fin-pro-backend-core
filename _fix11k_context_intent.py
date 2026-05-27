from pathlib import Path

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

old='''            primary_reply = p4_12_context_lock(primary_reply, message)'''

new='''            context_reply = p4_12_context_lock(primary_reply, message)
            if context_reply not in [None, ""]:
                primary_reply = context_reply'''

assert old in s, "CONTEXT_LOCK_PATCH_NOT_FOUND"
s=s.replace(old,new,1)

anchor='''            if not primary_reply:
                primary_reply = safe_reply(message)'''

inject='''            if not primary_reply:
                msg=(message or "").lower().strip()

                if any(x in msg for x in ["quem é você","quem é vc","quem e vc","quem e você","quem é voce","quem e voce"]):
                    primary_reply="Sou a Eldora 🙂 O que você quer saber?"

                elif any(x in msg for x in ["como você está","como vc está","vc está bem","tudo bem"]):
                    primary_reply="Tudo certo por aqui 🙂 E você?"

                elif "quanto é" in msg or any(x in msg for x in ["x","+","-","*","/"]):
                    primary_reply=safe_reply(message)

                elif any(x in msg for x in ["e depois","depois?"]):
                    primary_reply="Depois mantemos contexto, validamos o fluxo real e seguimos sem reset semântico."

                else:
                    primary_reply=safe_reply(message)'''

assert anchor in s, "SAFE_REPLY_ANCHOR_NOT_FOUND"
s=s.replace(anchor,inject,1)

p.write_text(s,encoding="utf-8")
print("FIX11K_CONTEXT_LOCK_AND_INTENT_RESCUE_OK")
