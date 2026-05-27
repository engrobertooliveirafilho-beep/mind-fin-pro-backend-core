from pathlib import Path
p=Path("app/main.py")
s=p.read_text(encoding="utf-8")
block='''

# FIX11K_C_SAFE_PROBE_ACTIVE
try:
    from app.runtime.fix11k_probe import install_fix11k_probe
    install_fix11k_probe(globals())
except Exception:
    pass
'''
if "FIX11K_C_SAFE_PROBE_ACTIVE" not in s:
    s=s.rstrip()+block+"
"
p.write_text(s,encoding="utf-8")
print("FIX11K_C_PATCHED")
