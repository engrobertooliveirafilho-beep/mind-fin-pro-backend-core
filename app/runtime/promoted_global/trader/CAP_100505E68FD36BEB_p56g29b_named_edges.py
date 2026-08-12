import os
import psycopg2

conn = psycopg2.connect(
    os.getenv("DATABASE_URL"),
    sslmode="require"
)

cur = conn.cursor()

cur.execute("""
SELECT
    e.relationship_type,
    e.validation_status,
    e.confidence_score,

    p.animal_name AS parent_name,
    c.animal_name AS child_name,

    e.parent_animal_id,
    e.child_animal_id,

    e.source_id

FROM p55a_pedigree_edges e
LEFT JOIN p55a_animals p
    ON p.id = e.parent_animal_id
LEFT JOIN p55a_animals c
    ON c.id = e.child_animal_id

ORDER BY e.confidence_score DESC
""")

rows = cur.fetchall()

print("EDGE_COUNT =", len(rows))

for r in rows:
    print(r)

cur.close()
conn.close()
