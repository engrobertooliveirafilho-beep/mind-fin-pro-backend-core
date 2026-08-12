from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

marker = "P19P31_P19P36_COMPANION_RUNTIME_ENRICHMENT"

if marker not in s:
    target = '''            if reply:
                return _p19p28m_twiml(reply)
'''
    replacement = '''            if reply:
                # P19P31_P19P36_COMPANION_RUNTIME_ENRICHMENT
                try:
                    from app.companionship.p19p31_p19p36_companion_runtime import compose_reply as _p19p31_compose_reply
                    reply = _p19p31_compose_reply(sender, body, ctxu, reply)
                except Exception:
                    pass
                # /P19P31_P19P36_COMPANION_RUNTIME_ENRICHMENT
                return _p19p28m_twiml(reply)
'''
    count = s.count(target)
    if count < 1:
        raise SystemExit("TARGET_REPLY_RETURN_BLOCK_NOT_FOUND")

    s = s.replace(target, replacement)

p.write_text(s, encoding="utf-8")
print("P19P31_P19P36_MAIN_INTEGRATION_OK")
