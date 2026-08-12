from pathlib import Path
import re

p = Path("app/runtime/forensic_bootstrap.py")
s = p.read_text(encoding="utf-8")

if "P19P28L_BOOTSTRAP_SINGLE_INSTALL_GUARD" not in s:
    guard = r'''
# P19P28L_BOOTSTRAP_SINGLE_INSTALL_GUARD
_P19P28L_BOOTSTRAP_INSTALLED = False

def p19p28l_bootstrap_already_installed():
    global _P19P28L_BOOTSTRAP_INSTALLED
    if _P19P28L_BOOTSTRAP_INSTALLED:
        try:
            event("P19P28L_BOOTSTRAP_DUPLICATE_BLOCKED", module_name=__name__)
        except Exception:
            pass
        return True
    _P19P28L_BOOTSTRAP_INSTALLED = True
    return False
# /P19P28L_BOOTSTRAP_SINGLE_INSTALL_GUARD
'''
    s = guard + "\n" + s

# inserir bloqueio no início da função de bootstrap mais provável
patterns = [
    r"(def\s+install_forensic_bootstrap\s*\([^)]*\):\n)",
    r"(def\s+bootstrap\s*\([^)]*\):\n)",
    r"(def\s+install\s*\([^)]*\):\n)",
]

inserted = False
for pat in patterns:
    m = re.search(pat, s)
    if m and "P19P28L_BOOTSTRAP_ENTRY_GUARD" not in s[m.end():m.end()+500]:
        call = "    # P19P28L_BOOTSTRAP_ENTRY_GUARD\n    if p19p28l_bootstrap_already_installed():\n        return {\"status\":\"already_installed\"}\n"
        s = s[:m.end()] + call + s[m.end():]
        inserted = True
        break

# se não houver função clara, criar função segura
if not inserted and "def install_forensic_bootstrap" not in s:
    s += r'''

def install_forensic_bootstrap():
    # P19P28L_BOOTSTRAP_ENTRY_GUARD
    if p19p28l_bootstrap_already_installed():
        return {"status":"already_installed"}
    try:
        event("FORENSIC_BOOTSTRAP_ACTIVE", module_name=__name__)
    except Exception:
        pass
    return {"status":"installed"}
'''

p.write_text(s, encoding="utf-8")
print("FORENSIC_BOOTSTRAP_PATCH_OK")
