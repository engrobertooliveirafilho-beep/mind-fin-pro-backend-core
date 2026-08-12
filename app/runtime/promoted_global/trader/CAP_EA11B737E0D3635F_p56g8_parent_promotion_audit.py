import os, psycopg2, json
from datetime import datetime, timezone

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

names=["Lady Luck","Whitewater Skoal","Bushwacker"]

cur.execute("""
SELECT id, official_name, confidence_score, validation_status, notes, created_at
FROM p55a_animals
WHERE official_name = ANY(%s)
ORDER BY official_name, confidence_score DESC
""",(names,))

animals=cur.fetchall()

snapshot={
    "mission":"P5.6G8_REAL_PARENT_PROMOTION_AUDIT",
    "created_at":datetime.now(timezone.utc).isoformat(),
    "mode":"AUDIT_ONLY_NO_MUTATION",
    "animals":[]
}

for animal_id,name,conf,status,notes,created_at in animals:
    cur.execute("SELECT COUNT(*) FROM p55a_media WHERE animal_id=%s",(animal_id,))
    media=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM p55a_biomechanics WHERE animal_id=%s",(animal_id,))
    bio=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM p55a_judge_scores WHERE animal_id=%s",(animal_id,))
    judge=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM p55a_reproduction_records WHERE animal_id=%s AND validation_status <> 'quarantined'",(animal_id,))
    rep=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM p55a_pedigree_edges WHERE parent_id=%s AND validation_status <> 'quarantined'",(animal_id,))
    ped=cur.fetchone()[0]

    promote = (name in ["Lady Luck","Whitewater Skoal"] and rep >= 1 and ped >= 1)

    snapshot["animals"].append({
        "id":str(animal_id),
        "official_name":name,
        "confidence_score":float(conf),
        "validation_status":status,
        "media":media,
        "biomechanics":bio,
        "judge_scores":judge,
        "active_reproduction_records":rep,
        "active_pedigree_edges_as_parent":ped,
        "promotion_candidate":promote,
        "recommended_status":"provisional" if promote else status
    })

open("P56G8_REAL_PARENT_PROMOTION_AUDIT.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False,default=str))
print(json.dumps(snapshot,indent=2,ensure_ascii=False,default=str))

conn.close()
