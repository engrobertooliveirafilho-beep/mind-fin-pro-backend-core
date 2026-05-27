from pathlib import Path
import re

# ==========================
# FIX 1 - _fix11k_trace lixo no middleware
# ==========================
p = Path("app/main.py")
txt = p.read_text(encoding="utf-8")

bad = [
    'mark(_fix11k_trace,"primary_raw",locals().get("reply"))',
    'mark(_fix11k_trace,"after_dispatch",locals().get("reply"))',
    'mark(_fix11k_trace,"after_ux_guard",locals().get("reply"))',
    'mark(_fix11k_trace,"after_context_lock",locals().get("reply"))',
    'mark(_fix11k_trace,"after_factual_lock",locals().get("reply"))',
    'mark(_fix11k_trace,"after_factual_handoff",locals().get("reply"))',
    'mark(_fix11k_trace,"after_sca",locals().get("reply"))',
    'mark(_fix11k_trace,"after_arbiter",locals().get("reply"))',
    'mark(_fix11k_trace,"before_normalize",locals().get("reply"))',
    'mark(_fix11k_trace,"after_normalize",locals().get("reply"))',
]

for b in bad:
    txt = txt.replace(b, "# FIX11K_REMOVED")

p.write_text(txt, encoding="utf-8")

# ==========================
# FIX 2 - shim wrap_callable
# ==========================
f = Path("app/runtime/forensic_trace.py")
t = f.read_text(encoding="utf-8")

if "def wrap_callable(" not in t:
    t += '''

def wrap_callable(fn):
    return fn
'''
    f.write_text(t, encoding="utf-8")

print("FIX11K_RUNTIME_PATCH_OK")
