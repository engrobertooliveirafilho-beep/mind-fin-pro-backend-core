$ErrorActionPreference="Stop"

@"
from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")

old='''            primary_reply = factual_search_handoff(primary_reply, message)

            authority_reply = strategic_conversation_authority(primary_reply, message)'''

new='''            primary_reply = factual_search_handoff(primary_reply, message)

            runtime_error_reply = any(x in str(primary_reply) for x in [
                "WEBHOOK_ERROR_TOTAL",
                "DATABASE_URL missing",
                "AssertionError",
                "Traceback"
            ])

            if runtime_error_reply:
                primary_reply = p412n_final_semantic_ux_guard(message, primary_reply)

            authority_reply = strategic_conversation_authority(primary_reply, message)'''

if old not in s:
    raise SystemExit("PATCH_POINT_NOT_FOUND")

s=s.replace(old,new,1)

old2='''            arbiter_reply = final_conversational_arbiter(sender_id, message, primary_reply)
            if arbiter_reply is not None:
                primary_reply = arbiter_reply'''

new2='''            if not runtime_error_reply:
                arbiter_reply = final_conversational_arbiter(sender_id, message, primary_reply)
                if arbiter_reply is not None:
                    primary_reply = arbiter_reply'''

s=s.replace(old2,new2,1)

p.write_text(s,encoding="utf-8")
print("FIX11K_RUNTIME_ERROR_GUARD_OK")
"@ | Set-Content "_fix11k_runtime_error_guard.py" -Encoding UTF8

python _fix11k_runtime_error_guard.py
python -m compileall -q app tests
pytest
python _replay_final_guard.py
git diff app/main.py
