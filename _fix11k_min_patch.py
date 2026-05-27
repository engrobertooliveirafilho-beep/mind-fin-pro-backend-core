from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

old='''primary_reply = strategic_conversation_authority(primary_reply, message)
            primary_reply = final_conversational_arbiter(sender_id, message, primary_reply)'''

new='''authority_reply = strategic_conversation_authority(primary_reply, message)
            if authority_reply is not None:
                primary_reply = authority_reply

            arbiter_reply = final_conversational_arbiter(sender_id, message, primary_reply)
            if arbiter_reply is not None:
                primary_reply = arbiter_reply'''

if old not in s:
    raise SystemExit("PATCH_TARGET_NOT_FOUND")

s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("PATCH_OK")
