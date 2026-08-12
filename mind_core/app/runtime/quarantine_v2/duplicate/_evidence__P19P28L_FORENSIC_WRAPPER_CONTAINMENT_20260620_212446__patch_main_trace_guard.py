from pathlib import Path

p = Path("app/main.py")
s = p.read_text(encoding="utf-8")

if "P19P28L_FIX11K_TRACE_SAFE_DEFAULT" not in s:
    marker = "from "
    inject = '''
# P19P28L_FIX11K_TRACE_SAFE_DEFAULT
try:
    _fix11k_trace
except NameError:
    _fix11k_trace = []
# /P19P28L_FIX11K_TRACE_SAFE_DEFAULT

'''
    idx = s.find(marker)
    if idx >= 0:
        s = s[:idx] + inject + s[idx:]
    else:
        s = inject + s

# blindar chamadas mark(_fix11k_trace...) se mark não existir
if "P19P28L_SAFE_MARK_DEFAULT" not in s:
    inject2 = '''
# P19P28L_SAFE_MARK_DEFAULT
try:
    mark
except NameError:
    def mark(trace, stage, value=None):
        try:
            trace.append({"stage": stage, "value": str(value)[:500]})
        except Exception:
            pass
# /P19P28L_SAFE_MARK_DEFAULT

'''
    token = "# /P19P28L_FIX11K_TRACE_SAFE_DEFAULT\n\n"
    s = s.replace(token, token + inject2)

p.write_text(s, encoding="utf-8")
print("MAIN_TRACE_GUARD_PATCH_OK")
