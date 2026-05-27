from pathlib import Path

p=Path("app/main.py")
lines=p.read_text(encoding="utf-8").splitlines()

for i in range(400,436):
    print(f"{i+1:04d}: {repr(lines[i])}")
