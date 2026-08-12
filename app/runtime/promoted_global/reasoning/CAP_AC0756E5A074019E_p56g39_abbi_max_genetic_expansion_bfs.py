import re, json, hashlib, requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timezone
from collections import deque

MISSION="P5.6G39_ABBI_MAX_GENETIC_EXPANSION_BFS"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

SEEDS=[
  {"name":"Bushwacker","abbi":"10058008","depth":0},
  {"name":"REINDEER","abbi":"10010628","depth":1},
  {"name":"MO 110","abbi":"10007793","depth":1},
  {"name":"NACCARATO BREEDING","abbi":"21","depth":2},
  {"name":"DIAMOND'S GHOST","abbi":"10000789","depth":2},
  {"name":"NACCARATO'S OSCARS VELVET","abbi":"10006436","depth":2},
  {"name":"JR 34","abbi":"10002937","depth":2},
  {"name":"RATJEN BREEDING","abbi":"39","depth":2},
  {"name":"UNKNOWN_DAM_REINDEER","abbi":"10004709","depth":2}
]

MAX_DEPTH=3
seen=set()
queue=deque(SEEDS)

profiles=[]
entity_candidates={}
edge_candidates=[]
blocked_edges=[]

def clean(text):
    return re.sub(r"\s+"," ",text).strip()

def parse_profile(text, abbi, url, depth):
    m=re.search(r"Animal Pedigree\s+(.+?)\s+Animal\s+ABBI#\s+(\d+)",text,re.I)
    animal=m.group(1).strip() if m else None
    registry=m.group(2).strip() if m else abbi

    profile={
      "animal":animal,
      "abbi":registry,
      "url":url,
      "depth":depth,
      "raw_context":text[text.lower().find("animal pedigree"):text.lower().find("phone:")] if "animal pedigree" in text.lower() else text[:1200],
      "parents":[],
      "status":"PARSED" if animal else "PARSE_WEAK"
    }

    ctx=profile["raw_context"]

    # padrão: ! SIRE DAM ABBI# sire_abbi dam_abbi
    pm=re.search(r"!\s+(.+?)\s+(.+?)\s+Sire\s+Dam\s+ABBI#\s+(\d+)\s+ABBI#\s+(\d+)",ctx,re.I)
    if pm:
        sire_name=pm.group(1).strip()
        dam_name=pm.group(2).strip()
        sire_abbi=pm.group(3).strip()
        dam_abbi=pm.group(4).strip()
        profile["parents"].append({"relation":"sire","parent":sire_name,"parent_abbi":sire_abbi})
        profile["parents"].append({"relation":"dam","parent":dam_name,"parent_abbi":dam_abbi})
    else:
        # padrão incompleto: ! NAME Sire Dam ABBI# num
        pm2=re.search(r"!\s+(.+?)\s+Sire\s+Dam\s+ABBI#\s+(\d+)",ctx,re.I)
        if pm2:
            profile["parents"].append({"relation":"sire","parent":pm2.group(1).strip(),"parent_abbi":pm2.group(2).strip()})
            blocked_edges.append({
              "child":animal,
              "child_abbi":registry,
              "relation":"dam",
              "reason":"DAM_NAME_OR_ABBI_MISSING_PUBLIC_PROFILE",
              "source_url":url
            })

    return profile

while queue:
    item=queue.popleft()
    abbi=item["abbi"]
    depth=item["depth"]

    if not abbi or abbi in seen or depth>MAX_DEPTH:
        continue

    seen.add(abbi)
    url=f"http://members.americanbuckingbull.com/bulls.aspx?id={abbi}"

    try:
        r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=60)
        html=r.text
        text=clean(BeautifulSoup(html,"html.parser").get_text(" ",strip=True))

        (out/f"{abbi}.html").write_text(html,encoding="utf-8")
        (out/f"{abbi}.txt").write_text(text,encoding="utf-8")

        p=parse_profile(text,abbi,url,depth)
        p["status_code"]=r.status_code
        p["sha256"]=hashlib.sha256(html.encode()).hexdigest()
        profiles.append(p)

        if p["animal"]:
            entity_candidates[p["abbi"]] = {
              "official_name":p["animal"],
              "registry_number":p["abbi"],
              "depth":depth,
              "source_url":url,
              "confidence_score":85 if depth<=2 else 75,
              "validation_status":"provisional"
            }

        for parent in p["parents"]:
            if parent["parent"] and parent["parent_abbi"]:
                edge_candidates.append({
                  "parent":parent["parent"],
                  "parent_abbi":parent["parent_abbi"],
                  "child":p["animal"],
                  "child_abbi":p["abbi"],
                  "relation":parent["relation"],
                  "depth":depth+1,
                  "confidence_score":85 if depth<=2 else 75,
                  "source_url":url,
                  "status":"CANDIDATE"
                })

                if parent["parent_abbi"] not in seen and depth+1<=MAX_DEPTH:
                    queue.append({
                      "name":parent["parent"],
                      "abbi":parent["parent_abbi"],
                      "depth":depth+1
                    })

    except Exception as e:
        profiles.append({
          "abbi":abbi,
          "depth":depth,
          "url":url,
          "status":"FETCH_FAILED",
          "error":repr(e)
        })

result={
  "mission":MISSION,
  "mode":"MAX_EXPANSION_EVIDENCE_ONLY_NO_DATABASE_WRITE",
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "max_depth":MAX_DEPTH,
  "summary":{
    "profiles_fetched":len([p for p in profiles if p.get("status_code")==200]),
    "profiles_total":len(profiles),
    "entity_candidates":len(entity_candidates),
    "edge_candidates":len(edge_candidates),
    "blocked_edges":len(blocked_edges)
  },
  "profiles":profiles,
  "entity_candidates":list(entity_candidates.values()),
  "edge_candidates":edge_candidates,
  "blocked_edges":blocked_edges,
  "status":"PASS"
}

(out/"P56G39_ABBI_MAX_GENETIC_EXPANSION_BFS.json").write_text(
  json.dumps(result,indent=2,ensure_ascii=False),
  encoding="utf-8"
)

print(json.dumps(result["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =", out)
