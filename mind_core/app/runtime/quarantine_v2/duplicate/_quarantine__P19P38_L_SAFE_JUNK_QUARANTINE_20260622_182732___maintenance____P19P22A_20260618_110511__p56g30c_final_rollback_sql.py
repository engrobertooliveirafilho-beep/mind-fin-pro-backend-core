import os
import psycopg2
import json
import uuid
from pathlib import Path

SOURCE_ID = "df645e3f-d3c9-4eed-a876-d79d052a6f99"

out = Path("reports/P5.6G30_CONTROLLED_PEDIGREE_MUTATION")
out.mkdir(parents=True, exist_ok=True)

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur = conn.cursor()

cur.execute("""
select id, official_name, registry_number, confidence_score, validation_status
from p55a_animals
where lower(official_name)=lower('Bushwacker')
order by confidence_score desc nulls last
""")
bush = cur.fetchall()

cur.execute("""
select id, source_url, confidence_score, validation_status, raw_payload
from p55a_sources
where id=%s
""", (SOURCE_ID,))
source = cur.fetchall()

blocked = False
blockers = []

reliable_bush = [r for r in bush if r[4] == "reliable"]
if len(reliable_bush) != 1:
    blocked = True
    blockers.append("Bushwacker did not resolve to exactly one reliable entity.")

if len(source) != 1:
    blocked = True
    blockers.append("Canonical ABBI source_id not found exactly once.")

for name, reg in [("REINDEER MO", "10010628"), ("110", "10007793")]:
    cur.execute("""
    select id, official_name, registry_number
    from p55a_animals
    where lower(official_name)=lower(%s) or registry_number=%s
    """, (name, reg))
    rows = cur.fetchall()
    if rows:
        blocked = True
        blockers.append(f"{name}/{reg} already exists: {rows}")

bush_id = reliable_bush[0][0] if reliable_bush else None

ids = {
    "reindeer_mo_id": str(uuid.uuid4()),
    "dam_110_id": str(uuid.uuid4()),
    "reindeer_edge_id": str(uuid.uuid4()),
    "dam_110_edge_id": str(uuid.uuid4())
}

report = {
    "mission": "P5.6G30C_FINAL_ROLLBACK_SQL",
    "mode": "FINAL_SQL_WITH_ROLLBACK_NO_COMMIT",
    "canonical_source_id": SOURCE_ID,
    "bushwacker_id": str(bush_id) if bush_id else None,
    "new_ids": ids,
    "blocked": blocked,
    "blockers": blockers
}

if not blocked:
    sql = f"""
-- P5.6G30C FINAL ROLLBACK SQL
-- SAFE MODE: ROLLBACK AT END
-- DO NOT CHANGE TO COMMIT WITHOUT MANUAL APPROVAL

BEGIN;

-- 1. Create ABBI parent entities

INSERT INTO p55a_animals
(id, official_name, registry_number, animal_type, sex, confidence_score, validation_status, notes)
VALUES
('{ids["reindeer_mo_id"]}', 'REINDEER MO', '10010628', 'bucking_bull', 'male', 85, 'reliable',
 'ABBI source {SOURCE_ID}: sire of Bushwacker ABBI#10058008.'),
('{ids["dam_110_id"]}', '110', '10007793', 'bucking_cattle', 'female', 85, 'reliable',
 'ABBI source {SOURCE_ID}: dam of Bushwacker ABBI#10058008.');

-- 2. Quarantine unsourced provisional conflicting edges

UPDATE p55a_pedigree_edges
SET validation_status='quarantined'
WHERE child_id='{bush_id}'
  AND relation='sire'
  AND validation_status='provisional'
  AND evidence_source_id IS NULL;

UPDATE p55a_pedigree_edges
SET validation_status='quarantined'
WHERE child_id='{bush_id}'
  AND relation='dam'
  AND validation_status='provisional'
  AND evidence_source_id IS NULL;

-- 3. Insert ABBI-backed pedigree edges

INSERT INTO p55a_pedigree_edges
(id, parent_id, child_id, relation, generation_distance, evidence_source_id, confidence_score, validation_status)
VALUES
('{ids["reindeer_edge_id"]}', '{ids["reindeer_mo_id"]}', '{bush_id}', 'sire', 1, '{SOURCE_ID}', 85, 'reliable'),
('{ids["dam_110_edge_id"]}', '{ids["dam_110_id"]}', '{bush_id}', 'dam', 1, '{SOURCE_ID}', 85, 'reliable');

-- 4. Validation snapshot inside transaction

SELECT
  e.relation,
  e.validation_status,
  e.confidence_score,
  p.official_name AS parent,
  c.official_name AS child,
  e.evidence_source_id
FROM p55a_pedigree_edges e
LEFT JOIN p55a_animals p ON p.id=e.parent_id
LEFT JOIN p55a_animals c ON c.id=e.child_id
WHERE c.id='{bush_id}'
ORDER BY e.validation_status, e.relation, e.confidence_score DESC;

ROLLBACK;
"""
else:
    sql = "-- BLOCKED. SQL not generated because preconditions failed.\n-- " + json.dumps(blockers, indent=2)

(out / "P56G30C_FINAL_ROLLBACK_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)
(out / "P56G30C_FINAL_ROLLBACK_SQL.sql").write_text(sql, encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))
print("SQL salvo em:", out / "P56G30C_FINAL_ROLLBACK_SQL.sql")

cur.close()
conn.close()
