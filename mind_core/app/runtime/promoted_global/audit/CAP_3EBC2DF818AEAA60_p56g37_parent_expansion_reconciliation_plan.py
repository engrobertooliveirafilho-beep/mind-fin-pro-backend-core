import os, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G37_PARENT_EXPANSION_RECONCILIATION_PLAN"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

targets=[
 ("REINDEER","REINDEER MO","10010628"),
 ("MO 110","110","10007793"),
 ("NACCARATO BREEDING AN 11",None,"21"),
 ("DIAMOND'S GHOST",None,"10000789"),
 ("NACCARATO'S OSCARS VELVET",None,"10006436"),
 ("JR 34",None,"10002937"),
 ("NACCARATO BREEDING",None,"21"),
 ("RATJEN BREEDING",None,"39")
]

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

resolution=[]
for name, current, reg in targets:
    cur.execute("""
    select id, official_name, registry_number, aliases, confidence_score, validation_status
    from p55a_animals
    where lower(official_name)=lower(%s)
       or registry_number=%s
       or (%s is not null and lower(official_name)=lower(%s))
    order by confidence_score desc nulls last
    """,(name,reg,current,current))
    rows=cur.fetchall()
    resolution.append({
      "target_name":name,
      "current_db_name":current,
      "registry_number":reg,
      "matches":[
        {
          "id":str(r[0]),
          "official_name":r[1],
          "registry_number":r[2],
          "aliases":r[3],
          "confidence_score":str(r[4]),
          "validation_status":r[5]
        } for r in rows
      ]
    })

plan={
 "mission":MISSION,
 "mode":"PLAN_ONLY_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "entity_resolution":resolution,
 "mutation_plan":[],
 "status":"READY_FOR_REVIEW"
}

for r in resolution:
    if not r["matches"]:
        plan["mutation_plan"].append({
          "action":"CREATE_ENTITY_CANDIDATE",
          "official_name":r["target_name"],
          "registry_number":r["registry_number"],
          "animal_type":"bull",
          "validation_status":"provisional",
          "confidence_score":80,
          "reason":"ABBI generation expansion evidence"
        })
    elif r["current_db_name"] and r["matches"]:
        existing=r["matches"][0]
        if existing["official_name"] != r["target_name"]:
            plan["mutation_plan"].append({
              "action":"NAME_ALIAS_RECONCILIATION",
              "existing_id":existing["id"],
              "current_name":existing["official_name"],
              "official_abbi_name":r["target_name"],
              "registry_number":r["registry_number"],
              "suggested_action":"ADD_ALIAS_OR_UPDATE_OFFICIAL_NAME_AFTER_REVIEW"
            })

plan["pedigree_edge_candidates"]=[
 {"parent":"NACCARATO BREEDING AN 11","parent_abbi":"21","child":"REINDEER","child_abbi":"10010628","relation":"sire","status":"CANDIDATE"},
 {"parent":"UNKNOWN_NAME","parent_abbi":"10004709","child":"REINDEER","child_abbi":"10010628","relation":"dam","status":"BLOCKED_NAME_MISSING"},
 {"parent":"DIAMOND'S GHOST","parent_abbi":"10000789","child":"MO 110","child_abbi":"10007793","relation":"sire","status":"CANDIDATE"},
 {"parent":"UNKNOWN_NAME","parent_abbi":None,"child":"MO 110","child_abbi":"10007793","relation":"dam","status":"MISSING"}
]

(out/"P56G37_PARENT_EXPANSION_RECONCILIATION_PLAN.json").write_text(
 json.dumps(plan, indent=2, ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps({
 "mission":MISSION,
 "entities_checked":len(resolution),
 "mutations_planned":len(plan["mutation_plan"]),
 "edge_candidates":len(plan["pedigree_edge_candidates"]),
 "status":plan["status"]
}, indent=2, ensure_ascii=False))

cur.close()
conn.close()
