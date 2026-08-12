import os, psycopg2, json
from datetime import datetime, timezone

bad_edge = "113db249-7804-4077-bcf9-564eea2a7a8c"

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

cur.execute("""
UPDATE p55a_pedigree_edges
SET validation_status='quarantined'
WHERE id=%s
RETURNING id
""",(bad_edge,))

rows=cur.fetchall()
conn.commit()

snapshot={
  "mission":"P5.6G11_QUARANTINE_EDGE_TO_WEAK_BUSHWACKER",
  "created_at":datetime.now(timezone.utc).isoformat(),
  "quarantined_edges":[str(x[0]) for x in rows]
}

open("P56G11_QUARANTINE_EDGE_TO_WEAK_BUSHWACKER.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2))
print(json.dumps(snapshot,indent=2))

conn.close()
