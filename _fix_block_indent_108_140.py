from pathlib import Path

p=Path("app/main.py")
lines=p.read_text(encoding="utf-8").splitlines()

# Corrige bloco específico 108-140:
# if/elif no nível 4 espaços; corpo no nível 8 espaços.
for i in range(107,140):
    if i >= len(lines): 
        continue
    stripped=lines[i].lstrip()
    if not stripped:
        lines[i]=""
    elif stripped.startswith("if ") or stripped.startswith("elif "):
        lines[i]="    "+stripped
    else:
        lines[i]="        "+stripped

p.write_text("\n".join(lines)+"\n",encoding="utf-8")
print("BLOCK_108_140_INDENT_FIXED")
