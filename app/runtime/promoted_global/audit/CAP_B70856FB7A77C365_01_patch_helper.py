from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

helper = r'''
# P19P30D_LEGACY_INTERCEPTOR_CONTAINMENT
def _p19p30d_has_universal_context(sender_id):
    try:
        from app.context_runtime.universal_domain_context import get as _p19p30d_get_ctx
        ctx = _p19p30d_get_ctx(sender_id or "unknown")
        return bool(ctx and ctx.get("active_domain"))
    except Exception:
        return False

def _p19p30d_is_short_followup_text(text):
    try:
        t = str(text or "").lower().strip()
        return t in {
            "quais", "quais?", "quais são", "quais sao", "quais são?", "quais sao?",
            "prossiga", "continue", "continua", "e depois", "e depois?",
            "explique melhor", "detalhe", "detalha", "próximo passo", "proximo passo"
        }
    except Exception:
        return False
# /P19P30D_LEGACY_INTERCEPTOR_CONTAINMENT

'''

if "P19P30D_LEGACY_INTERCEPTOR_CONTAINMENT" not in s:
    marker = "# P19P28M_MAIN_PRE_ROUTER_FITNESS_LOCK"
    if marker not in s:
        raise SystemExit("MARKER_P19P28M_NOT_FOUND")
    s = s.replace(marker, helper + marker, 1)

p.write_text(s, encoding="utf-8")
print("P19P30D_HELPER_OK")
