from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

old = '''        if mode in ["followup", "new_domain"] and ctxu.get("active_domain"):
            reply = _p19p29_route_domain_reply(body, ctxu)
            if reply:
                return _p19p28m_twiml(reply)
'''

new = '''        if mode in ["followup", "new_domain"] and ctxu.get("active_domain"):
            reply = _p19p29_route_domain_reply(body, ctxu)
            if reply:
                return _p19p28m_twiml(reply)

        # P19P30D_CONTEXT_FIRST_SHORT_FOLLOWUP_ARBITER
        if _p19p30d_is_short_followup_text(body) and ctxu.get("active_domain"):
            reply = _p19p29_route_domain_reply(body, ctxu)
            if reply:
                return _p19p28m_twiml(reply)
        # /P19P30D_CONTEXT_FIRST_SHORT_FOLLOWUP_ARBITER
'''

if "P19P30D_CONTEXT_FIRST_SHORT_FOLLOWUP_ARBITER" not in s:
    if old not in s:
        raise SystemExit("P19P29_CONTEXT_BLOCK_NOT_FOUND")
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("P19P30D_PREROUTER_ARBITER_OK")
