from pathlib import Path
import json, datetime
from app.mind.p5_6f1_animal_discovery_engine.engine import AnimalDiscoveryEngine
from app.mind.p5_5z_executive_snapshot.snapshot import ExecutiveSnapshot

p=Path("app/mind/p5_6f1_animal_discovery_engine/engine.py")
s=p.read_text(encoding="utf-8")

s=s.replace(
'"descendants","progeny"]',
'"descendants","progeny","berger","barker","counting down","1995","tan","reference","industry","also first","photos","we re","we\\'re","best"]'
)

old='''    if n in {"list","com","site","www","bull","bucking","official","profile"}: return False
'''

new='''    if n in {"list","com","site","www","bull","bucking","official","profile","berger","barker","tan","reference","industry","dna","clone"}: return False
    if re.search(r"\\d", n): return False
'''

if old not in s:
    raise SystemExit("V3_BLOCK_NOT_FOUND")

p.write_text(s.replace(old,new),encoding="utf-8")

result=AnimalDiscoveryEngine().run_once(2600,3)
snap=ExecutiveSnapshot().build()

audit={
    "mission":"P5.6F1_DISCOVERY_HARDENING_V3_FREEZE",
    "created_at":datetime.datetime.now(datetime.UTC).isoformat(),
    "result":result,
    "snapshot_counts":snap["counts"],
    "critical_gaps":snap.get("critical_gaps")
}

open("p56f1_discovery_hardening_v3_freeze.json","w",encoding="utf-8").write(json.dumps(audit,ensure_ascii=False,indent=2,default=str))

print(json.dumps({
    "mission":audit["mission"],
    "candidates_found":result.get("candidates_found"),
    "promoted":result.get("promoted"),
    "top_candidates":result.get("top_candidates",[])[:15],
    "counts":audit["snapshot_counts"],
    "critical_gaps":audit["critical_gaps"]
},indent=2,ensure_ascii=False,default=str))
