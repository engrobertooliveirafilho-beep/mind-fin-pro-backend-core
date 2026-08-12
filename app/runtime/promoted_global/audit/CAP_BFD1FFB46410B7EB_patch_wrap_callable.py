from pathlib import Path
p = Path("app/runtime/forensic_trace.py")
s = p.read_text(encoding="utf-8")

start = s.find("def wrap_callable(")
if start >= 0:
    end = s.find("# /P19P28L_IDEMPOTENT_WRAP_CALLABLE", start)
    if end >= 0:
        end = end + len("# /P19P28L_IDEMPOTENT_WRAP_CALLABLE")
        s = s[:start] + s[end:]

if "P19P28M_WRAP_CALLABLE_VARARGS" not in s:
    s += r'''

# P19P28M_WRAP_CALLABLE_VARARGS
def wrap_callable(fn, *args, **kwargs):
    """
    Compatible idempotent wrapper.
    Accepts legacy signatures: wrap_callable(fn), wrap_callable(fn, name), wrap_callable(module, attr, fn).
    """
    if fn is None:
        return None

    target = fn
    name = None

    if len(args) >= 2 and callable(args[1]):
        target = args[1]
        name = str(args[0])
    elif len(args) >= 1:
        name = str(args[0])

    if getattr(target, "_p19p28m_wrapped", False):
        return target

    def _wrapped(*a, **k):
        try:
            event("P19P28M_WRAPPED_CALL", callable=name or getattr(target, "__name__", "unknown"))
        except Exception:
            pass
        return target(*a, **k)

    try:
        _wrapped.__name__ = getattr(target, "__name__", "_wrapped")
        _wrapped.__doc__ = getattr(target, "__doc__", None)
        _wrapped._p19p28m_wrapped = True
        _wrapped._p19p28m_original = target
    except Exception:
        pass

    return _wrapped
# /P19P28M_WRAP_CALLABLE_VARARGS
'''
p.write_text(s, encoding="utf-8")
print("WRAP_CALLABLE_VARARGS_OK")
