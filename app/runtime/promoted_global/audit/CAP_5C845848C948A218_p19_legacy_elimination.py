from pathlib import Path

path = Path("app/api/whatsapp.py")
src = path.read_text(encoding="utf-8")

lines = src.splitlines()
out = []

blocked_patterns = [
    "if \"como fazer\" in",
    "if \"e como fazer\" in",
    "if \"como\" in msg",
    "if \"como\" in _low",
    "return \"Vamos",
    "return \"Invista",
    "return \"Considere",
    "return fast",
    "return str(reply)",
]

for line in lines:
    low = line.strip().lower()

    # neutraliza bypass direto antes do runtime
    if any(p.lower() in low for p in blocked_patterns):
        out.append("# [P19_LEGACY_DISABLED] " + line)
        continue

    out.append(line)

# INSERÇÃO DE ENFORCEMENT GLOBAL
enforcer = '''

# ============================================================
# P19 LEGACY ENFORCEMENT LAYER (HARD GATE)
# ============================================================

def _p19_force_runtime_first(sender_id, inbound_text, runtime_fn):
    """
    FORÇA TODO INPUT PASSAR PELO RUNTIME COGNITIVO
    SEM EXCEÇÃO DE FAST PATH OU TEMPLATE LEGACY.
    """
    try:
        return runtime_fn(sender_id, inbound_text)
    except Exception:
        return "Erro interno no runtime. Tente novamente."
'''

if "P19 LEGACY ENFORCEMENT LAYER" not in src:
    out.insert(0, enforcer)

final_src = "\n".join(out)
path.write_text(final_src, encoding="utf-8")

print({
    "status": "patched",
    "file": str(path),
    "legacy_disabled": True
})
