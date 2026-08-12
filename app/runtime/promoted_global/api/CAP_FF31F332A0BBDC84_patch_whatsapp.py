from pathlib import Path

p = Path("app/api/whatsapp.py")
s = p.read_text(encoding="utf-8")

inject = '''
# P19P28H_G_K_CONTEXTUAL_FITNESS_RUNTIME
try:
    from app.domains.fitness_runtime import is_fitness as _p19p28_is_fitness
    from app.domains.fitness_runtime import is_fitness_followup as _p19p28_is_fitness_followup
    from app.domains.fitness_runtime import reply as _p19p28_fitness_reply
    from app.context_runtime.p19p28_context import bind as _p19p28_bind
    from app.context_runtime.p19p28_context import get as _p19p28_get
except Exception:
    _p19p28_is_fitness = None
    _p19p28_is_fitness_followup = None
    _p19p28_fitness_reply = None
    _p19p28_bind = None
    _p19p28_get = None

def _p19p28_pre_context_router(sender_id, inbound_text):
    txt = inbound_text or ""
    sid = sender_id or "unknown"

    if not _p19p28_is_fitness:
        return None

    if _p19p28_is_fitness(txt):
        if _p19p28_bind:
            _p19p28_bind(sid, "fitness", txt)
        return _p19p28_fitness_reply(txt)

    ctx = _p19p28_get(sid) if _p19p28_get else {}
    if ctx.get("active_domain") == "fitness" and _p19p28_is_fitness_followup(txt):
        return _p19p28_fitness_reply(txt)

    return None
# /P19P28H_G_K_CONTEXTUAL_FITNESS_RUNTIME
'''

if "P19P28H_G_K_CONTEXTUAL_FITNESS_RUNTIME" not in s:
    marker = "from "
    idx = s.find(marker)
    if idx >= 0:
        s = s[:idx] + inject + "\n" + s[idx:]
    else:
        s = inject + "\n" + s

call = '''
    # P19P28H_G_K_PRE_ROUTER_CALL
    try:
        _p19p28_direct = _p19p28_pre_context_router(sender_id, inbound_text)
        if _p19p28_direct:
            return _p19p9_universal_whatsapp_output_guard(inbound_text, _p19p28_direct, "")
    except Exception:
        pass
'''

if "P19P28H_G_K_PRE_ROUTER_CALL" not in s:
    target = '    _p19h3_text = str(inbound_text or "").lower().strip()'
    if target in s:
        s = s.replace(target, call + "\n" + target)
    else:
        raise SystemExit("TARGET_INSERT_POINT_NOT_FOUND")

old = '    if _p19h3_text in ["quais são", "quais sao", "quais?", "quais são?", "quais sao?"]:'
new = '    if _p19h3_text in ["quais são", "quais sao", "quais?", "quais são?", "quais sao?"] and not ((_p19p28_get(sender_id) if _p19p28_get else {}).get("active_domain")):'
s = s.replace(old, new)

p.write_text(s, encoding="utf-8")
print("WHATSAPP_PATCH_OK")
