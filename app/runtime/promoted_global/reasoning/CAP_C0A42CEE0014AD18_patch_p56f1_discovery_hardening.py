from pathlib import Path

p=Path("app/mind/p5_6f1_animal_discovery_engine/engine.py")
s=p.read_text(encoding="utf-8")

old='''BAD_CANDIDATE_TERMS = ["price","sale","auction","score","history","biography","offspring","pedigree","sire","dam","semen","http","https","rodeo","rider","riders","professional","american","year","old","youtube","top","riding","greatest","point","genetics","sell","three-time","production","inc","red","baddest","legendary","yeti","provided","won","first ever","record-breaking","dangerous","joe berger","1996"]'''

new='''BAD_CANDIDATE_TERMS = ["price","sale","auction","score","history","biography","offspring","pedigree","sire","dam","semen","http","https","rodeo","rider","riders","professional","american","year","old","youtube","top","riding","greatest","point","genetics","sell","three-time","production","inc","red","baddest","legendary","yeti","provided","won","first ever","record-breaking","dangerous","joe berger","1996","list","com","site","www","official","profile","connection","catalog","registration","number","stats","news","article","videos","watch","search"]'''

if old not in s:
    raise SystemExit("BAD_CANDIDATE_TERMS_BLOCK_NOT_FOUND")

s=s.replace(old,new)

old2='''    if len(n.split()) > 4: return False
    return True
'''

new2='''    if len(n.split()) > 4: return False
    if n in {"list","com","site","www","bull","bucking","official","profile"}: return False
    if "." in n or "/" in n or "_" in n: return False
    return True
'''

if old2 not in s:
    raise SystemExit("VALIDATION_BLOCK_NOT_FOUND")

p.write_text(s.replace(old2,new2),encoding="utf-8")
print("P5.6F1_DISCOVERY_HARDENED")
