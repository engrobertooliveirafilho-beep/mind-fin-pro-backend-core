import os, json, psycopg2
from datetime import datetime, timezone

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

tables=[
"p55a_animals",
"p55a_pedigree_edges",
"p55a_valuation_events",
"p55a_reproduction_records"
]

snapshot={
"mission":"P5.6F9_POST_QUARANTINE_FINAL_AUDIT",
"created_at":datetime.now(timezone.utc).isoformat(),
"tables":{}
}

for t in tables:
    cur.execute(f"""
    SELECT validation_status, COUNT(*)
    FROM {t}
    GROUP BY validation_status
    ORDER BY validation_status
    """)
    snapshot["tables"][t]={str(k):v for k,v in cur.fetchall()}

cur.execute("""
SELECT a.official_name,p.relation,b.official_name,p.confidence_score,p.validation_status
FROM p55a_pedigree_edges p
JOIN p55a_animals a ON a.id=p.parent_id
JOIN p55a_animals b ON b.id=p.child_id
WHERE p.validation_status <> 'quarantined'
ORDER BY a.official_name,b.official_name
""")
snapshot["active_pedigree_edges"]=cur.fetchall()

cur.execute("""
SELECT r.id,a.official_name,s.official_name,d.official_name,o.official_name,r.confidence_score,r.validation_status
FROM p55a_reproduction_records r
LEFT JOIN p55a_animals a ON a.id=r.animal_id
LEFT JOIN p55a_animals s ON s.id=r.sire_id
LEFT JOIN p55a_animals d ON d.id=r.dam_id
LEFT JOIN p55a_animals o ON o.id=r.offspring_id
WHERE r.validation_status <> 'quarantined'
ORDER BY r.created_at
""")
snapshot["active_reproduction_records"]=[tuple(str(x) if x is not None else None for x in row) for row in cur.fetchall()]

open("P56F9_POST_QUARANTINE_FINAL_AUDIT.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False,default=str))
print(json.dumps(snapshot,indent=2,ensure_ascii=False,default=str))

conn.close()
