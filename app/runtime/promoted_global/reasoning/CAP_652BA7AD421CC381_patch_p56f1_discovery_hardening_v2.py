from pathlib import Path

p=Path("app/mind/p5_6f1_animal_discovery_engine/engine.py")
s=p.read_text(encoding="utf-8")

s=s.replace(
'"search"]',
'"search","two-time","most unridden","breeding program","embryo transfer","owner breeder","breeding fee","clone","dna","as a","great","nfr","calves","descendants","progeny"]'
)

old='''    if re.search(r"\\b(of|and|the|was|in|for|with|from|to|by)\\b", n): return False
'''

new='''    if re.search(r"\\b(of|and|the|was|in|for|with|from|to|by|as|a|most|great|fee|owner|breeder|program|embryo|transfer|clone|dna|nfr)\\b", n): return False
'''

if old not in s:
    raise SystemExit("REGEX_BLOCK_NOT_FOUND")

s=s.replace(old,new)
p.write_text(s,encoding="utf-8")
print("P5.6F1_DISCOVERY_HARDENING_V2_DONE")
