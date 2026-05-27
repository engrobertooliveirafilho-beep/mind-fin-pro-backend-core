from pathlib import Path
import re

p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

# authority guard
s=re.sub(
r'primary_reply\s*=\s*strategic_conversation_authority\(primary_reply,\s*message\)',
'''authority_reply = strategic_conversation_authority(primary_reply, message)
            if authority_reply not in [None, ""]:
                primary_reply = authority_reply''',
s,
count=1
)

# arbiter guard
s=re.sub(
r'primary_reply\s*=\s*final_conversational_arbiter\(sender_id,\s*message,\s*primary_reply\)',
'''arbiter_reply = final_conversational_arbiter(sender_id, message, primary_reply)
            if arbiter_reply not in [None, ""]:
                primary_reply = arbiter_reply''',
s,
count=1
)

p.write_text(s,encoding="utf-8")
print("FIX11K_REPLY_LOCK_REGEX_OK")
