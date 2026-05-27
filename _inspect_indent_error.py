from pathlib import Path
p=Path("app/main.py")
lines=p.read_text(encoding="utf-8").splitlines()

for i in range(95,118):
    print(f"{i+1:04d}: {lines[i]}")
