import os, json, psycopg2
from datetime import datetime, timezone

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

cur.execute("""
SELECT
    child.official_name AS animal,
    sire.official_name AS sire,
    dam.official_name AS dam
FROM p55a_reproduction_records r
LEFT JOIN p55a_animals child ON child.id=r.offspring_id
LEFT JOIN p55a_animals sire ON sire.id=r.sire_id
LEFT JOIN p55a_animals dam ON dam.id=r.dam_id
WHERE r.validation_status <> 'quarantined'
ORDER BY animal
""")

bloodlines=[]
for animal,sire,dam in cur.fetchall():
    bloodlines.append({
        "animal": animal,
        "sire": sire,
        "dam": dam,
        "bloodline_status": "PROVISIONAL_REAL"
    })

cur.execute("""
SELECT COUNT(*)
FROM p55a_animals
WHERE validation_status <> 'quarantined'
""")
active_animals=cur.fetchone()[0]

cur.execute("""
SELECT COUNT(*)
FROM p55a_pedigree_edges
WHERE validation_status <> 'quarantined'
""")
active_edges=cur.fetchone()[0]

snapshot={
    "mission":"P5.6G0_REAL_BLOODLINE_CORE_SNAPSHOT",
    "created_at":datetime.now(timezone.utc).isoformat(),
    "active_animals":active_animals,
    "active_pedigree_edges":active_edges,
    "bloodlines":bloodlines,
    "conclusion":"Only Bushwacker has active verified sire/dam links after quarantine."
}

open("P56G0_REAL_BLOODLINE_CORE_SNAPSHOT.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False))
print(json.dumps(snapshot,indent=2,ensure_ascii=False))

conn.close()
