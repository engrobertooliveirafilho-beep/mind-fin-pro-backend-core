import os
import psycopg2
import json
from pathlib import Path

conn = psycopg2.connect(
    os.getenv("DATABASE_URL"),
    sslmode="require"
)

cur = conn.cursor()

cur.execute("""
SELECT
    e.id,
    e.relation,
    e.validation_status,
    e.confidence_score,
    p.official_name AS parent_name,
    c.official_name AS child_name,
    p.registry_number AS parent_registry,
    c.registry_number AS child_registry,
    e.parent_id,
    e.child_id,
    e.evidence_source_id,
    e.created_at
FROM p55a_pedigree_edges e
LEFT JOIN p55a_animals p ON p.id = e.parent_id
LEFT JOIN p55a_animals c ON c.id = e.child_id
ORDER BY c.official_name, e.relation, e.confidence_score DESC
""")

rows = cur.fetchall()

out = Path("reports/P5.6G29_PEDIGREE_RECONCILIATION")
out.mkdir(parents=True, exist_ok=True)

data = []
for r in rows:
    rec = {
        "edge_id": str(r[0]),
        "relation": r[1],
        "validation_status": r[2],
        "confidence_score": str(r[3]),
        "parent_name": r[4],
        "child_name": r[5],
        "parent_registry": r[6],
        "child_registry": r[7],
        "parent_id": str(r[8]),
        "child_id": str(r[9]),
        "evidence_source_id": str(r[10]) if r[10] else None,
        "created_at": str(r[11])
    }
    data.append(rec)

(out / "P56G29B_NAMED_PEDIGREE_EDGES.json").write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("EDGE_COUNT =", len(data))

for r in data:
    print(r["validation_status"], r["relation"], r["parent_name"], "->", r["child_name"], "conf=", r["confidence_score"], "src=", r["evidence_source_id"])

cur.close()
conn.close()
