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

ph = ",".join(["%s"] * len(trash_names))

cur.execute(f"""
SELECT id, official_name
FROM p55a_animals
WHERE official_name IN ({ph})
ORDER BY official_name
""", trash_names)

trash_animals = cur.fetchall()
trash_ids = [str(x[0]) for x in trash_animals]

cur.execute("""
SELECT id
FROM p55a_pedigree_edges
WHERE validation_status='weak'
   OR confidence_score <= 35
   OR parent_id = child_id
ORDER BY created_at
""")

bad_edge_ids = [str(x[0]) for x in cur.fetchall()]

cur.execute("""
SELECT id
FROM p55a_valuation_events
WHERE animal_id = ANY(%s::uuid[])
ORDER BY created_at
""", (trash_ids,))

bad_valuation_ids = [str(x[0]) for x in cur.fetchall()]

snapshot = {
    "mission": "P5.6F6_QUARANTINE_EXECUTION_PLAN",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "mode": "PLAN_ONLY_NO_MUTATION",
    "trash_animals": len(trash_ids),
    "bad_pedigree_edges": len(bad_edge_ids),
    "bad_valuation_events": len(bad_valuation_ids),
    "trash_animals_detail": [
        {"id": str(i), "official_name": n}
        for i,n in trash_animals
    ]
}

with open("P56F6_QUARANTINE_EXECUTION_PLAN.json","w",encoding="utf-8") as f:
    json.dump(snapshot,f,indent=2,ensure_ascii=False)

def uuid_array(ids):
    return "ARRAY[" + ",".join("'" + x + "'::uuid" for x in ids) + "]"

execution_sql = f"""
-- P5.6F6 QUARANTINE EXECUTION PLAN
-- MODE: NOT EXECUTED
-- Generated at: {snapshot["created_at"]}

BEGIN;

-- 1. Quarantine contaminated valuation events
UPDATE p55a_valuation_events
SET validation_status = 'quarantined'
WHERE id = ANY({uuid_array(bad_valuation_ids)});

-- 2. Quarantine contaminated pedigree edges
UPDATE p55a_pedigree_edges
SET validation_status = 'quarantined'
WHERE id = ANY({uuid_array(bad_edge_ids)});

-- 3. Quarantine semantic trash animals
UPDATE p55a_animals
SET validation_status = 'quarantined',
    notes = COALESCE(notes,'') || ' | P5.6F6 semantic trash quarantine candidate'
WHERE id = ANY({uuid_array(trash_ids)});

COMMIT;
"""

rollback_sql = f"""
-- P5.6F6 QUARANTINE ROLLBACK PLAN
-- MODE: NOT EXECUTED

BEGIN;

UPDATE p55a_animals
SET validation_status = 'provisional'
WHERE id = ANY({uuid_array(trash_ids)});

UPDATE p55a_pedigree_edges
SET validation_status = 'weak'
WHERE id = ANY({uuid_array(bad_edge_ids)});

UPDATE p55a_valuation_events
SET validation_status = 'provisional'
WHERE id = ANY({uuid_array(bad_valuation_ids)});

COMMIT;
"""

open("P56F6_QUARANTINE_EXECUTION_PLAN.sql","w",encoding="utf-8").write(execution_sql)
open("P56F6_QUARANTINE_ROLLBACK_PLAN.sql","w",encoding="utf-8").write(rollback_sql)

print(json.dumps(snapshot,indent=2,ensure_ascii=False))
print("FILES_CREATED:")
print("P56F6_QUARANTINE_EXECUTION_PLAN.json")
print("P56F6_QUARANTINE_EXECUTION_PLAN.sql")
print("P56F6_QUARANTINE_ROLLBACK_PLAN.sql")

conn.close()
