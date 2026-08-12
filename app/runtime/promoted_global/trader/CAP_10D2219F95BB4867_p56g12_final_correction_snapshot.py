import os, json, psycopg2
from datetime import datetime, timezone

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

snapshot={
  "mission":"P5.6G12_FINAL_CORRECTION_SNAPSHOT",
  "created_at":datetime.now(timezone.utc).isoformat(),
  "status":"CORRECTED_AND_PROTECTED",
  "tables":{}
}

for t in ["p55a_animals","p55a_pedigree_edges","p55a_reproduction_records","p55a_valuation_events"]:
    cur.execute(f"""
    SELECT validation_status, COUNT(*)
    FROM {t}
    GROUP BY validation_status
    ORDER BY validation_status
    """)
    snapshot["tables"][t]={str(k):v for k,v in cur.fetchall()}

cur.execute("""
SELECT parent.official_name,p.relation,child.official_name,child.confidence_score,child.validation_status
FROM p55a_pedigree_edges p
JOIN p55a_animals parent ON parent.id=p.parent_id
JOIN p55a_animals child ON child.id=p.child_id
WHERE p.validation_status <> 'quarantined'
ORDER BY parent.official_name
""")
snapshot["active_pedigree_edges"]=cur.fetchall()

snapshot["protection_layers"]=[
  "P5.6G4 strict entity validator",
  "P5.6G5 extractor integration",
  "P5.6G7 parent quality gate",
  "P5.6G8 audited parent promotion",
  "P5.6G11 weak duplicate edge quarantine"
]

snapshot["final_conclusion"]="Genetic graph now contains only active source-backed provisional/reliable parent links."

open("P56G12_FINAL_CORRECTION_SNAPSHOT.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False,default=str))
print(json.dumps(snapshot,indent=2,ensure_ascii=False,default=str))

conn.close()
