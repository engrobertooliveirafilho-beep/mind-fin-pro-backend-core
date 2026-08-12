from pathlib import Path
import re

p = Path("app/runtime/fix11k_probe.py")
s = p.read_text(encoding="utf-8")

pattern = r"def wrap_callable\(fn,[\s\S]*?(?=\ndef |\nclass |\Z)"
replacement = r'''
# P19P28N_FIX11K_WRAP_CALLABLE_VARARGS
def wrap_callable(fn, *args, **kwargs):
    """
    Compatível com chamadas:
    - wrap_callable(fn)
    - wrap_callable(fn, name)
    - wrap_callable(module, attr, fn)
    """
    target = fn
    name = None

    if len(args) >= 2 and callable(args[1]):
        name = str(args[0])
        target = args[1]
    elif len(args) >= 1:
        name = str(args[0])

    if target is None:
        return None

    if getattr(target, "_p19p28n_wrapped", False):
        return target

    def _wrapped(*a, **k):
        return target(*a, **k)

    try:
        _wrapped.__name__ = getattr(target, "__name__", "_wrapped")
        _wrapped.__doc__ = getattr(target, "__doc__", None)
        _wrapped._p19p28n_wrapped = True
        _wrapped._p19p28n_original = target
        _wrapped._p19p28n_name = name
    except Exception:
        pass

    return _wrapped
# /P19P28N_FIX11K_WRAP_CALLABLE_VARARGS

'''

if "P19P28N_FIX11K_WRAP_CALLABLE_VARARGS" not in s:
    s2, n = re.subn(pattern, replacement, s, count=1)
    if n == 0:
        s2 = replacement + "\n" + s
    s = s2

p.write_text(s, encoding="utf-8")
print("FIX11K_WRAP_CALLABLE_PATCH_OK")
