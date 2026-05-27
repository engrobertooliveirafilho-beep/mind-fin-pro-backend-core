$ErrorActionPreference="Stop"

@"
from pathlib import Path
import re

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

# 1) proteger context lock vazio
s=re.sub(
r'primary_reply\s*=\s*p4_12_context_lock\(primary_reply,\s*message\)',
'''context_reply = p4_12_context_lock(primary_reply, message)
            if context_reply not in [None, ""]:
                primary_reply = context_reply''',
s,
count=1
)

# 2) rescue final por intent ANTES do fallback
anchor='''if not primary_reply:
                primary_reply = safe_reply(message)'''

inject='''if not primary_reply:
                msg=(message or "").lower().strip()

                if any(x in msg for x in ["quem é você","quem é vc","quem e vc","quem e você"]):
                    primary_reply="Sou a Eldora 🙂 O que você quer saber?"

                elif any(x in msg for x in ["como você está","vc está bem","tudo bem"]):
                    primary_reply="Tudo certo por aqui 🙂 E você?"

                elif ("quanto é" in msg or re.search(r'\\d+\\s*([xX*+\\-/])\\s*\\d+',msg)):
                    primary_reply=safe_reply(message)

                elif any(x in msg for x in ["e depois","depois?"]):
                    primary_reply="Depois mantemos contexto, validamos o fluxo real e seguimos sem reset semântico."

                else:
                    primary_reply = safe_reply(message)'''

if anchor not in s:
    raise SystemExit("FALLBACK_ANCHOR_NOT_FOUND")

s=s.replace(anchor,inject,1)

p.write_text(s,encoding="utf-8")
print("FIX11K_INTENT_RESCUE_OK")
"@ | Set-Content "_fix11k_intent_rescue.py" -Encoding UTF8

python _fix11k_intent_rescue.py
python -m py_compile app/main.py
pytest
python _replay_final_guard.py
git diff app/main.py
