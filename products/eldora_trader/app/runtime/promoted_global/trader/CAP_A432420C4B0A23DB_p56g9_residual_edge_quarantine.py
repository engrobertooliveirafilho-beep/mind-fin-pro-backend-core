import os, psycopg2, json
from datetime import datetime, timezone

bad_parents=[
'TBB 8460',
'Showtime',
'JATT 4702 Original Breeder',
'J31A Bodacious DAM',
'Bodacious Daughter Lot',
'E40 Black',
'GLC687'
]

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

cur.execute("""
UPDATE p55a_pedigree_edges p
SET validation_status='quarantined'
FROM p55a_animals a
WHERE p.parent_id=a.id
AND a.official_name = ANY(%s)
RETURNING p.id,a.official_name,p.relation,p.child_id
""",(bad_parents,))

rows=cur.fetchall()
conn.commit()

snapshot={
"mission":"P5.6G9_RESIDUAL_WEAK_PARENT_EDGE_QUARANTINE",
"created_at":datetime.now(timezone.utc).isoformat(),
"quarantined_edges":len(rows),
"details":[tuple(str(x) for x in r) for r in rows]
}

open("P56G9_RESIDUAL_WEAK_PARENT_EDGE_QUARANTINE.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False))
print(json.dumps(snapshot,indent=2,ensure_ascii=False))

conn.close()
