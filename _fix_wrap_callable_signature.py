from pathlib import Path
p=Path("app/runtime/forensic_trace.py")
s=p.read_text(encoding="utf-8")
import re
s=re.sub(
    r"def wrap_callable\(fn\):\n\s+return fn",
    "def wrap_callable(fn, *args, **kwargs):\n    return fn",
    s
)
p.write_text(s,encoding="utf-8")
print("WRAP_CALLABLE_SIGNATURE_FIXED")
