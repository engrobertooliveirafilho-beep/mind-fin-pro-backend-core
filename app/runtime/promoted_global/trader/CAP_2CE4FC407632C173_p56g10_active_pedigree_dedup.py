import os, psycopg2, json
from datetime import datetime, timezone

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

cur.execute("""
WITH ranked AS (
  SELECT
    id,
    ROW_NUMBER() OVER (
      PARTITION BY parent_id, child_id, relation
      ORDER BY created_at ASC
    ) rn
  FROM p55a_pedigree_edges
  WHERE validation_status <> 'quarantined'
)
UPDATE p55a_pedigree_edges p
SET validation_status='quarantined'
FROM ranked r
WHERE p.id=r.id
AND r.rn > 1
RETURNING p.id
""")

rows=cur.fetchall()
conn.commit()

snapshot={
  "mission":"P5.6G10_ACTIVE_PEDIGREE_DEDUP",
  "created_at":datetime.now(timezone.utc).isoformat(),
  "quarantined_duplicate_edges":len(rows),
  "ids":[str(x[0]) for x in rows]
}

open("P56G10_ACTIVE_PEDIGREE_DEDUP.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2))
print(json.dumps(snapshot,indent=2))

conn.close()
