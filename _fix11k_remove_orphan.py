from pathlib import Path
import re

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

lines=s.splitlines()

clean=[]
for i,l in enumerate(lines, start=1):
    if i>=600 and (
        "authority_reply = strategic_conversation_authority" in l or
        "arbiter_reply = final_conversational_arbiter" in l or
        'if authority_reply not in [None, ""]:' in l or
        'if arbiter_reply not in [None, ""]:' in l or
        'primary_reply = authority_reply' in l or
        'primary_reply = arbiter_reply' in l
    ):
        continue
    clean.append(l)

p.write_text("\n".join(clean),encoding="utf-8")
print("FIX11K_REMOVE_ORPHAN_BLOCK_OK")
