from pathlib import Path

# =========================
# FIX 1 - main.py indent
# =========================
p=Path("app/main.py")
lines=p.read_text(encoding="utf-8").splitlines()

# linhas 97-140 devem estar dentro do interceptor (4 espaços)
for i in range(96,140):  # zero-based
    if i < len(lines):
        ln=lines[i]
        if ln and not ln.startswith("    "):
            lines[i]="    "+ln

# bloco da linha 108+ estava com indent sobrando (8); normalizar para 4
for i in range(107,140):
    if i < len(lines):
        ln=lines[i]
        while ln.startswith("        "):
            ln=ln[4:]
        lines[i]="    "+ln.lstrip()

p.write_text("\n".join(lines)+"\n",encoding="utf-8")

# =========================
# FIX 2 - forensic_trace.event
# =========================
p2=Path("app/runtime/forensic_trace.py")
s=p2.read_text(encoding="utf-8")

if "def event(" not in s:
    s += '''

def event(name, **kwargs):
    try:
        payload = {
            "event": name,
            "ts": time.time(),
            **kwargs
        }
        p = TRACE_DIR / "events.jsonl"
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\\n")
    except Exception:
        pass
'''
p2.write_text(s,encoding="utf-8")

print("FIX_RENDER_IMPORT_OK")
