from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

anchor='''            primary_reply = factual_search_handoff(primary_reply, message)'''

inject='''            primary_reply = factual_search_handoff(primary_reply, message)

            runtime_error_reply = any(x in str(primary_reply) for x in [
                "WEBHOOK_ERROR_TOTAL",
                "DATABASE_URL missing",
                "AssertionError",
                "Traceback"
            ])

            if runtime_error_reply:
                primary_reply = p412n_final_semantic_ux_guard(message, primary_reply)
            else:'''

if "runtime_error_reply" not in s:
    s=s.replace(anchor, inject, 1)

old='''            authority_reply = strategic_conversation_authority(primary_reply, message)
            if authority_reply is not None:
                primary_reply = authority_reply

            arbiter_reply = final_conversational_arbiter(sender_id, message, primary_reply)
            if arbiter_reply is not None:
                primary_reply = arbiter_reply'''

new='''                authority_reply = strategic_conversation_authority(primary_reply, message)
                if authority_reply is not None:
                    primary_reply = authority_reply

                arbiter_reply = final_conversational_arbiter(sender_id, message, primary_reply)
                if arbiter_reply is not None:
                    primary_reply = arbiter_reply'''

s=s.replace(old,new,1)

p.write_text(s,encoding="utf-8")
print("FIX11K_RUNTIME_ERROR_KILLSWITCH_OK")
