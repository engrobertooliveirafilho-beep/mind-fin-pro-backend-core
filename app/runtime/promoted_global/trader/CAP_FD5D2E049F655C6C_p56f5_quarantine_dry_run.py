import os
import json
import psycopg2
from datetime import datetime, timezone

trash_names = [
"adding established genetics along with cu",
"calves because of his",
"clicking your rodeo region below",
"Competition Stats",
"Competition Stats http",
"Daniels",
"Darci Miller",
"GLC",
"his 66 total outs",
"owner Julio Moreno in Merced",
"Page 463",
"Page 77",
"professional Getty Images",
"Sammy Andrews Breeding https",
"the",
"the cow Lady Luck",
"the Professional Bull Riders",
"Unknown. More Bulls",
"World Champion Bucking Bull"
]

conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
cur = conn.cursor()

placeholders = ",".join(["%s"] * len(trash_names))

cur.execute(f"""
SELECT id, official_name
FROM p55a_animals
WHERE official_name IN ({placeholders})
ORDER BY official_name
""", trash_names)

trash_animals = cur.fetchall()
trash_ids = [r[0] for r in trash_animals]

cur.execute("""
SELECT p.id, a.official_name, p.relation, b.official_name, p.confidence_score, p.validation_status
FROM p55a_pedigree_edges p
JOIN p55a_animals a ON a.id=p.parent_id
JOIN p55a_animals b ON b.id=p.child_id
WHERE p.validation_status='weak'
   OR p.confidence_score <= 35
   OR p.parent_id = p.child_id
ORDER BY a.official_name,b.official_name
""")

bad_edges = cur.fetchall()

impact = {
    "mission": "P5.6F5_QUARANTINE_PLAN_DRY_RUN",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "mode": "DRY_RUN_NO_MUTATION",
    "trash_animals_count": len(trash_animals),
    "trash_animals": [{"id": str(i), "official_name": n} for i,n in trash_animals],
    "bad_edges_count": len(bad_edges),
    "bad_edges": [
        {
            "id": str(eid),
            "parent": parent,
            "relation": relation,
            "child": child,
            "confidence_score": float(conf),
            "validation_status": status
        }
        for eid,parent,relation,child,conf,status in bad_edges
    ]
}

for table,col in [
    ("p55a_media","animal_id"),
    ("p55a_biomechanics","animal_id"),
    ("p55a_judge_scores","animal_id"),
    ("p55a_valuation_events","animal_id"),
    ("p55a_reproduction_records","animal_id")
]:
    if trash_ids:
        cur.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {col} = ANY(%s::uuid[])",
            (trash_ids,)
        )
        impact[f"{table}_linked_to_trash"] = cur.fetchone()[0]

with open("P56F5_QUARANTINE_PLAN_DRY_RUN.json","w",encoding="utf-8") as f:
    json.dump(impact,f,indent=2,ensure_ascii=False)

print(json.dumps(impact,indent=2,ensure_ascii=False))

conn.close()
