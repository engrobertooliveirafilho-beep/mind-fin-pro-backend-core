from pathlib import Path

def dump(path,start,end):
    print("="*120)
    print(path)
    lines=Path(path).read_text(encoding="utf-8").splitlines()
    for i in range(start-1,end):
        if i < len(lines):
            print(f"{i+1:04d}: {lines[i]}")

dump("app/main.py",90,140)
dump("app/runtime/forensic_trace.py",1,120)
