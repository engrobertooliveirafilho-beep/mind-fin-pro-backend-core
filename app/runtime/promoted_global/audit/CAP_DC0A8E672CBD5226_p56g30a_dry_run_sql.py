import os
import psycopg2
import json
import uuid
from pathlib import Path

out = Path("reports/P5.6G30_CONTROLLED_PEDIGREE_MUTATION")
out.mkdir(parents=True, exist_ok=True)

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur = conn.cursor()

# Resolver Bushwacker confiável
cur.execute("""
select id, official_name, registry_number, confidence_score, validation_status
from p55a_animals
where lower(official_name) = lower('Bushwacker')
order by confidence_score desc nulls last
""")
bush = cur.fetchall()

# Verificar pais ABBI
targets = ["REINDEER MO", "110"]
parents = {}
for t in targets:
    cur.execute("""
    select id, official_name, registry_number, confidence_score, validation_status
    from p55a_animals
    where lower(official_name)=lower(%s) or registry_number=%s
    """, (t, "10010628" if t=="REINDEER MO" else "10007793"))
    parents[t] = cur.fetchall()

# Verificar edges conflitantes
cur.execute("""
select e.id, p.official_name, c.official_name, e.relation, e.validation_status, e.evidence_source_id
from p55a_pedigree_edges e
left join p55a_animals p on p.id=e.parent_id
left join p55a_animals c on c.id=e.child_id
where lower(c.official_name)=lower('Bushwacker')
""")
edges = cur.fetchall()

dry_run = {
  "mission": "P5.6G30A_DRY_RUN_SQL",
  "mode": "DRY_RUN_NO_DATABASE_WRITE",
  "bushwacker_matches": [list(map(str, r)) for r in bush],
  "parent_matches": {k:[list(map(str, r)) for r in v] for k,v in parents.items()},
  "current_bushwacker_edges": [list(map(str, r)) for r in edges],
  "new_ids": {
    "reindeer_mo_id": str(uuid.uuid4()),
    "dam_110_id": str(uuid.uuid4()),
    "reindeer_edge_id": str(uuid.uuid4()),
    "dam_110_edge_id": str(uuid.uuid4())
  },
  "blocked": False,
  "blockers": []
}

if len([r for r in bush if r[4] == "reliable"]) != 1:
    dry_run["blocked"] = True
    dry_run["blockers"].append("Bushwacker did not resolve to exactly one reliable entity.")

if parents["REINDEER MO"]:
    dry_run["blocked"] = True
    dry_run["blockers"].append("REINDEER MO already exists or registry_number already exists.")

if parents["110"]:
    dry_run["blocked"] = True
    dry_run["blockers"].append("110 already exists or registry_number already exists.")

bush_id = bush[0][0] if bush else None
ids = dry_run["new_ids"]

sql = f"""
-- P5.6G30A DRY RUN SQL
-- DO NOT EXECUTE WITHOUT FINAL APPROVAL

BEGIN;

INSERT INTO p55a_animals
(id, official_name, registry_number, animal_type, sex, confidence_score, validation_status, notes)
VALUES
('{ids["reindeer_mo_id"]}', 'REINDEER MO', '10010628', 'bucking_bull', 'male', 85, 'reliable',
 'Created from ABBI pedigree page for Bushwacker ABBI#10058008.'),
('{ids["dam_110_id"]}', '110', '10007793', 'bucking_cattle', 'female', 85, 'reliable',
 'Created from ABBI pedigree page for Bushwacker ABBI#10058008.');

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

INSERT INTO p55a_pedigree_edges
(id, parent_id, child_id, relation, generation_distance, evidence_source_id, confidence_score, validation_status)
VALUES
('{ids["reindeer_edge_id"]}', '{ids["reindeer_mo_id"]}', '{bush_id}', 'sire', 1, NULL, 85, 'reliable'),
('{ids["dam_110_edge_id"]}', '{ids["dam_110_id"]}', '{bush_id}', 'dam', 1, NULL, 85, 'reliable');

ROLLBACK;
"""

(out / "P56G30A_DRY_RUN_REPORT.json").write_text(json.dumps(dry_run, indent=2, ensure_ascii=False), encoding="utf-8")
(out / "P56G30A_DRY_RUN_SQL.sql").write_text(sql, encoding="utf-8")

print(json.dumps(dry_run, indent=2, ensure_ascii=False))
print("\nSQL salvo em:", out / "P56G30A_DRY_RUN_SQL.sql")

cur.close()
conn.close()
