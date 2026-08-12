import os

ROOTS = [
    "app/eldora",
    "app/human",
    "app/humanization",
    "app/friendship",
    "app/memory",
    "app/persona",
]

KEYS = [
    "memory","social","identity","relationship",
    "emotion","trust","attachment","timeline",
    "learning","planning","reflection"
]

hits = {}

for r in ROOTS:
    if not os.path.exists(r):
        continue

    for base,_,files in os.walk(r):
        for f in files:
            if not f.endswith(".py"):
                continue

            p = os.path.join(base,f)

            try:
                txt = open(p,"r",encoding="utf-8",errors="ignore").read().lower()
            except:
                continue

            matched = [k for k in KEYS if k in txt]
            if matched:
                for m in matched:
                    hits.setdefault(m, []).append(p)

collisions = {k:v for k,v in hits.items() if len(v) > 1}

print("COLLISIONS:")
for k,v in collisions.items():
    print(k, len(v))
    for p in v[:5]:
        print(" -", p)
