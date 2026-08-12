import os, json, psycopg2
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("reports/P5.6G30_CONTROLLED_PEDIGREE_MUTATION")
OUT.mkdir(parents=True, exist_ok=True)

CANONICAL_SOURCE_ID = "df645e3f-d3c9-4eed-a876-d79d052a6f99"
BUSHWACKER_ID = "fc55d337-491f-458f-b962-d8cc6372a0fb"

REINDEER_MO_ID = "5a87cfa3-c33e-463c-9b5c-30b997d1b962"
DAM_110_ID = "d64d1a1f-01dd-4587-bf18-bf8e3c968cfc"

REINDEER_EDGE_ID = "40e1c5b0-a279-4f2e-baa4-b54435c2f5c8"
DAM_110_EDGE_ID = "65fb2c59-e33c-4629-8146-83f85cc8bdb2"

REPORT = OUT / "p56g30d_existing_node_relink_plan.json"
SQL_OUT = OUT / "P56G30D_EXISTING_NODE_RELINK_ROLLBACK.sql"

def q(cur, sql, args):
    cur.execute(sql, args)
    return cur.fetchall()

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur = conn.cursor()

checks = {}

cur.execute("select id, name, registration_number from animals where id=%s", (REINDEER_MO_ID,))
checks["reindeer_mo_node"] = cur.fetchall()

cur.execute("select id, name, registration_number from animals where id=%s", (DAM_110_ID,))
checks["dam_110_node"] = cur.fetchall()

cur.execute("select id, name, registration_number from animals where id=%s", (BUSHWACKER_ID,))
checks["bushwacker_node"] = cur.fetchall()

cur.execute("""
select id, source_animal_id, target_animal_id, relationship_type
from animal_relationships
where source_animal_id=%s and target_animal_id=%s
""", (BUSHWACKER_ID, REINDEER_MO_ID))
checks["existing_reindeer_edges"] = cur.fetchall()

cur.execute("""
select id, source_animal_id, target_animal_id, relationship_type
from animal_relationships
where source_animal_id=%s and target_animal_id=%s
""", (BUSHWACKER_ID, DAM_110_ID))
checks["existing_dam_110_edges"] = cur.fetchall()

blocked = False
blockers = []

if not checks["reindeer_mo_node"]:
    blocked = True
    blockers.append("REINDEER_MO_NODE_NOT_FOUND")

if not checks["dam_110_node"]:
    blocked = True
    blockers.append("DAM_110_NODE_NOT_FOUND")

if not checks["bushwacker_node"]:
    blocked = True
    blockers.append("BUSHWACKER_NODE_NOT_FOUND")

sql_lines = [
    "-- P5.6G30D_EXISTING_NODE_RELINK_PLAN",
    "-- MODE: ROLLBACK ONLY / NO COMMIT",
    "BEGIN;",
]

if not checks["existing_reindeer_edges"]:
    sql_lines.append(f"""
insert into animal_relationships (id, source_animal_id, target_animal_id, relationship_type, created_at)
values ('{REINDEER_EDGE_ID}', '{BUSHWACKER_ID}', '{REINDEER_MO_ID}', 'SIRE', now());
""")
else:
    sql_lines.append("-- REINDEER MO edge already exists. No insert required.")

if not checks["existing_dam_110_edges"]:
    sql_lines.append(f"""
insert into animal_relationships (id, source_animal_id, target_animal_id, relationship_type, created_at)
values ('{DAM_110_EDGE_ID}', '{BUSHWACKER_ID}', '{DAM_110_ID}', 'DAM', now());
""")
else:
    sql_lines.append("-- 110 edge already exists. No insert required.")

sql_lines.extend([
    "",
    "-- Verification query",
    f"""
select id, source_animal_id, target_animal_id, relationship_type
from animal_relationships
where source_animal_id='{BUSHWACKER_ID}'
and target_animal_id in ('{REINDEER_MO_ID}', '{DAM_110_ID}');
""",
    "",
    "ROLLBACK;",
])

SQL_OUT.write_text("\n".join(sql_lines), encoding="utf-8")

report = {
    "mission": "P5.6G30D_EXISTING_NODE_RELINK_PLAN",
    "mode": "ROLLBACK_SQL_NO_COMMIT",
    "blocked": blocked,
    "blockers": blockers,
    "canonical_source_id": CANONICAL_SOURCE_ID,
    "bushwacker_id": BUSHWACKER_ID,
    "existing_nodes": {
        "reindeer_mo_id": REINDEER_MO_ID,
        "dam_110_id": DAM_110_ID
    },
    "existing_edges": {
        "reindeer_mo": len(checks["existing_reindeer_edges"]),
        "dam_110": len(checks["existing_dam_110_edges"])
    },
    "sql_file": str(SQL_OUT),
    "next": "AUDIT_SQL_THEN_EXECUTE_ROLLBACK_ONLY" if not blocked else "FIX_BLOCKERS",
    "generated_at": datetime.now(timezone.utc).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

cur.close()
conn.close()

print(json.dumps(report, indent=2, ensure_ascii=False))
print(f"SQL salvo em: {SQL_OUT}")
