from pathlib import Path

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

# PATCH 1 — context lock
target='primary_reply = p4_12_context_lock(primary_reply, message)'
assert target in s, "TARGET_CONTEXT_NOT_FOUND"

s=s.replace(
target,
'''context_reply = p4_12_context_lock(primary_reply, message)
            if context_reply not in [None, ""]:
                primary_reply = context_reply''',
1
)

# PATCH 2 — rescue final
target2='primary_reply = safe_reply(message)'
assert target2 in s, "SAFE_REPLY_NOT_FOUND"

s=s.replace(
target2,
'''msg=(message or "").lower().strip()

                if any(x in msg for x in ["quem é você","quem é vc","quem e vc","quem e você","quem é voce","quem e voce"]):
                    primary_reply="Sou a Eldora 🙂 O que você quer saber?"

                elif any(x in msg for x in ["como você está","como vc está","vc está bem","tudo bem"]):
                    primary_reply="Tudo certo por aqui 🙂 E você?"

                elif "quanto é" in msg:
                    primary_reply=safe_reply(message)

                elif any(x in msg for x in ["e depois","depois?"]):
                    primary_reply="Depois mantemos contexto, validamos o fluxo real e seguimos sem reset semântico."

                else:
                    primary_reply=safe_reply(message)''',
1
)

p.write_text(s,encoding="utf-8")
print("FIX11K_CONTEXT_RESCUE_ENTERED")
