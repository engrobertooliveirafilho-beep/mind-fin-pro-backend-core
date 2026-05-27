from pathlib import Path

p=Path("app/main.py")
lines=p.read_text(encoding="utf-8").splitlines()

start=107  # zero-based = linha 108
end=len(lines)

for idx in range(start, len(lines)):
    line=lines[idx]
    if idx > start and (line.startswith("def ") or line.startswith("@app.") or line.startswith("async def ")):
        end=idx
        break

for i in range(start,end):
    if lines[i].startswith("        "):
        lines[i]=lines[i][4:]

p.write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"DEDENT_OK lines {start+1}-{end}")
