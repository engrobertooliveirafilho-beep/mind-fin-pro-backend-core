from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")
old="""            primary_reply = strategic_conversation_authority(primary_reply, message)
            primary_reply = final_conversational_arbiter(sender_id, message, primary_reply)"""
new="""            authority_reply = strategic_conversation_authority(primary_reply, message)
            if authority_reply not in [None, ""]:
                primary_reply = authority_reply

            arbiter_reply = final_conversational_arbiter(sender_id, message, primary_reply)
            if arbiter_reply not in [None, ""]:
                primary_reply = arbiter_reply"""
assert old in s, "PATCH_TARGET_NOT_FOUND"
p.write_text(s.replace(old,new,1),encoding="utf-8")
print("FIX11K_REPLY_LOCK_OK")
