from pathlib import Path

p = Path("app/runtime/forensic_trace.py")
s = p.read_text(encoding="utf-8") if p.exists() else ""

if "P19P28L_IDEMPOTENT_WRAP_CALLABLE" not in s:
    s += r'''

# P19P28L_IDEMPOTENT_WRAP_CALLABLE
def wrap_callable(fn, name=None):
    """
    Idempotent wrapper guard.
    Prevents recursive/double wrapping of runtime callables.
    """
    if fn is None:
        return None

    if getattr(fn, "_p19p28l_wrapped", False):
        return fn

    def _wrapped(*args, **kwargs):
        try:
            event("P19P28L_WRAPPED_CALL", callable=name or getattr(fn, "__name__", "unknown"))
        except Exception:
            pass
        return fn(*args, **kwargs)

    try:
        _wrapped.__name__ = getattr(fn, "__name__", "_wrapped")
        _wrapped.__doc__ = getattr(fn, "__doc__", None)
        _wrapped._p19p28l_wrapped = True
        _wrapped._p19p28l_original = fn
    except Exception:
        pass

    return _wrapped
# /P19P28L_IDEMPOTENT_WRAP_CALLABLE
'''
p.write_text(s, encoding="utf-8")
print("FORENSIC_TRACE_PATCH_OK")
