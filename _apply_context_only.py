from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

target="            primary_reply = p4_12_context_lock(primary_reply, message)"
assert target in s, "CONTEXT_TARGET_NOT_FOUND"

s=s.replace(target, """            context_reply = p4_12_context_lock(primary_reply, message)
            if context_reply not in [None, ""]:
                primary_reply = context_reply""", 1)

p.write_text(s,encoding="utf-8")
print("CONTEXT_REPLY_LOCK_WRITTEN")
