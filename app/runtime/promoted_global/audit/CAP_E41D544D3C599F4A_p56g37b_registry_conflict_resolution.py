import os, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone

MISSION="P5.6G37B_REGISTRY_CONFLICT_RESOLUTION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True, exist_ok=True)

registry_numbers=["21","39","10000789","10002937","10006436","10004709"]

conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur=conn.cursor()

result={
  "mission":MISSION,
  "mode":"AUDIT_ONLY_NO_DATABASE_WRITE",
  "generated_at":datetime.now(timezone.utc).isoformat(),
  "registry_checks":[],
  "status":"UNKNOWN",
  "blockers":[]
}

for reg in registry_numbers:
    cur.execute("""
    select id, official_name, registry_number, aliases, confidence_score, validation_status
    from p55a_animals
    where registry_number=%s
    order by confidence_score desc nulls last
    """,(reg,))
    rows=cur.fetchall()
    result["registry_checks"].append({
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

# conflito interno do plano
planned=[
 ("NACCARATO BREEDING AN 11","21"),
 ("NACCARATO BREEDING","21"),
 ("RATJEN BREEDING","39"),
 ("DIAMOND'S GHOST","10000789"),
 ("JR 34","10002937"),
 ("NACCARATO'S OSCARS VELVET","10006436")
]

seen={}
for name,reg in planned:
    if reg in seen:
        result["blockers"].append({
          "type":"PLANNED_DUPLICATE_REGISTRY",
          "registry_number":reg,
          "entities":[seen[reg],name]
        })
    else:
        seen[reg]=name

result["status"]="BLOCKED" if result["blockers"] else "PASS"

(out/"P56G37B_REGISTRY_CONFLICT_RESOLUTION.json").write_text(
 json.dumps(result,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps(result,indent=2,ensure_ascii=False))

cur.close()
conn.close()
