from pathlib import Path
import re

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

inject = r'''
# P19P28M_MAIN_PRE_ROUTER_FITNESS_LOCK
try:
    from starlette.responses import Response
    from urllib.parse import parse_qs
    from app.domains.fitness_runtime import is_fitness as _p19p28m_is_fitness
    from app.domains.fitness_runtime import is_fitness_followup as _p19p28m_is_fitness_followup
    from app.domains.fitness_runtime import reply as _p19p28m_fitness_reply
    from app.context_runtime.p19p28_context import bind as _p19p28m_bind
    from app.context_runtime.p19p28_context import get as _p19p28m_get
except Exception:
    Response = None
    parse_qs = None
    _p19p28m_is_fitness = None
    _p19p28m_is_fitness_followup = None
    _p19p28m_fitness_reply = None
    _p19p28m_bind = None
    _p19p28m_get = None

def _p19p28m_twiml(msg: str):
    return Response(
        content=f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{msg}</Message></Response>',
        media_type="application/xml"
    )

async def _p19p28m_main_pre_router(request):
    if request.url.path != "/webhook/whatsapp" or request.method.upper() != "POST":
        return None
    if not _p19p28m_is_fitness or not parse_qs or not Response:
        return None

    raw = await request.body()
    data = parse_qs(raw.decode("utf-8", errors="ignore"))
    body = (data.get("Body", [""])[0] or "").strip()
    sender = (data.get("From", ["unknown"])[0] or "unknown").strip()

    if _p19p28m_is_fitness(body):
        if _p19p28m_bind:
            _p19p28m_bind(sender, "fitness", body)
        return _p19p28m_twiml(_p19p28m_fitness_reply(body))

    ctx = _p19p28m_get(sender) if _p19p28m_get else {}
    if ctx.get("active_domain") == "fitness" and _p19p28m_is_fitness_followup(body):
        return _p19p28m_twiml(_p19p28m_fitness_reply(body))

    return None
# /P19P28M_MAIN_PRE_ROUTER_FITNESS_LOCK

'''

if "P19P28M_MAIN_PRE_ROUTER_FITNESS_LOCK" not in s:
    idx = s.find("from ")
    if idx >= 0:
        s = s[:idx] + inject + "\n" + s[idx:]
    else:
        s = inject + "\n" + s

# inserir no primeiro middleware HTTP antes de call_next
if "P19P28M_MAIN_PRE_ROUTER_CALL" not in s:
    m = re.search(r'(@app\.middleware\("http"\)\s*\n\s*async def [^(]+\([^)]*\):\s*\n)', s)
    if not m:
        raise SystemExit("HTTP_MIDDLEWARE_NOT_FOUND")

    call = '''
    # P19P28M_MAIN_PRE_ROUTER_CALL
    try:
        _p19p28m_response = await _p19p28m_main_pre_router(request)
        if _p19p28m_response is not None:
            return _p19p28m_response
    except Exception:
        pass

'''
    s = s[:m.end()] + call + s[m.end():]

p.write_text(s, encoding="utf-8")
print("MAIN_PRE_ROUTER_PATCH_OK")
