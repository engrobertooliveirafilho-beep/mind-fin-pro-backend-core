import os, json, psycopg2
from datetime import datetime, timezone

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

cur.execute("""
SELECT
    a.id,
    a.official_name,
    a.confidence_score,
    a.validation_status,
    COALESCE(media.c,0) AS media_count,
    COALESCE(bio.avg_score,0) AS avg_biomechanics,
    COALESCE(judge.avg_score,0) AS avg_judge,
    COALESCE(ped.c,0) AS active_pedigree_edges,
    COALESCE(rep.c,0) AS active_reproduction_records
FROM p55a_animals a
LEFT JOIN (
    SELECT animal_id, COUNT(*) c
    FROM p55a_media
    GROUP BY animal_id
) media ON media.animal_id=a.id
LEFT JOIN (
    SELECT animal_id, AVG(biomechanics_score) avg_score
    FROM p55a_biomechanics
    GROUP BY animal_id
) bio ON bio.animal_id=a.id
LEFT JOIN (
    SELECT animal_id, AVG(mind_bull_score) avg_score
    FROM p55a_judge_scores
    GROUP BY animal_id
) judge ON judge.animal_id=a.id
LEFT JOIN (
    SELECT parent_id animal_id, COUNT(*) c
    FROM p55a_pedigree_edges
    WHERE validation_status <> 'quarantined'
    GROUP BY parent_id
) ped ON ped.animal_id=a.id
LEFT JOIN (
    SELECT animal_id, COUNT(*) c
    FROM p55a_reproduction_records
    WHERE validation_status <> 'quarantined'
    GROUP BY animal_id
) rep ON rep.animal_id=a.id
WHERE a.validation_status <> 'quarantined'
ORDER BY a.official_name
""")

rows=cur.fetchall()

results=[]

for animal_id,name,conf,status,media,bio,judge,ped,rep in rows:
    score = float(conf or 0) + float(media or 0)*2 + float(bio or 0)*0.25 + float(judge or 0)*0.5 + float(ped or 0)*5 + float(rep or 0)*5
    results.append({
        "animal_id":str(animal_id),
        "official_name":name,
        "validation_status":status,
        "post_quarantine_score":round(score,4),
        "confidence_score":float(conf or 0),
        "media_count":media,
        "avg_biomechanics":round(float(bio or 0),4),
        "avg_judge":round(float(judge or 0),4),
        "active_pedigree_edges":ped,
        "active_reproduction_records":rep
    })

results=sorted(results,key=lambda x:x["post_quarantine_score"],reverse=True)

snapshot={
    "mission":"P5.6G2_POST_QUARANTINE_VALUATION_RECALC",
    "created_at":datetime.now(timezone.utc).isoformat(),
    "mode":"RECALC_NO_DB_MUTATION",
    "active_animals_scored":len(results),
    "top_20":results[:20]
}

open("P56G2_POST_QUARANTINE_VALUATION_RECALC.json","w",encoding="utf-8").write(json.dumps(snapshot,indent=2,ensure_ascii=False))
print(json.dumps(snapshot,indent=2,ensure_ascii=False))

conn.close()
