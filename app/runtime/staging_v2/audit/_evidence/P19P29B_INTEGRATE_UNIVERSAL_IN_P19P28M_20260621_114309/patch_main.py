from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

old = '''    if _p19p28m_is_fitness(body):
        if _p19p28m_bind:
            _p19p28m_bind(sender, "fitness", body)
        return _p19p28m_twiml(_p19p28m_fitness_reply(body))

    ctx = _p19p28m_get(sender) if _p19p28m_get else {}
    if ctx.get("active_domain") == "fitness" and _p19p28m_is_fitness_followup(body):
        return _p19p28m_twiml(_p19p28m_fitness_reply(body))

    return None
'''

new = '''    # P19P29B_UNIVERSAL_CONTEXT_INSIDE_P19P28M
    try:
        from app.context_runtime.universal_domain_context import resolve as _p19p29_resolve
        from app.domains.universal_domain_router import route_domain_reply as _p19p29_route_domain_reply

        resolved = _p19p29_resolve(sender, body)
        mode = resolved.get("mode")
        ctxu = resolved.get("context") or {}

        if mode == "followup" and not resolved.get("has_context"):
            return _p19p28m_twiml("Sobre qual assunto? Preciso do tópico exato para continuar sem inventar contexto.")

        if mode in ["followup", "new_domain"] and ctxu.get("active_domain"):
            reply = _p19p29_route_domain_reply(body, ctxu)
            if reply:
                return _p19p28m_twiml(reply)
    except Exception:
        pass
    # /P19P29B_UNIVERSAL_CONTEXT_INSIDE_P19P28M

    if _p19p28m_is_fitness(body):
        if _p19p28m_bind:
            _p19p28m_bind(sender, "fitness", body)
        return _p19p28m_twiml(_p19p28m_fitness_reply(body))

    ctx = _p19p28m_get(sender) if _p19p28m_get else {}
    if ctx.get("active_domain") == "fitness" and _p19p28m_is_fitness_followup(body):
        return _p19p28m_twiml(_p19p28m_fitness_reply(body))

    return None
'''

if old not in s:
    raise SystemExit("P19P28M_TARGET_BLOCK_NOT_FOUND")

if "P19P29B_UNIVERSAL_CONTEXT_INSIDE_P19P28M" not in s:
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("P19P29B_MAIN_INTEGRATION_OK")
