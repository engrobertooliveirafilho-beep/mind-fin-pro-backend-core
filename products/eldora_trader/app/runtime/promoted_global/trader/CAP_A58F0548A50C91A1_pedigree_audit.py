import os
import psycopg2

conn = psycopg2.connect(
    os.environ["DATABASE_URL"],
    sslmode="require"
)

cur = conn.cursor()

cur.execute("""
SELECT
    p.id,
    a.official_name AS parent,
    p.relation,
    b.official_name AS child,
    p.generation_distance,
    p.confidence_score,
    p.validation_status
FROM p55a_pedigree_edges p
JOIN p55a_animals a
    ON a.id = p.parent_id
JOIN p55a_animals b
    ON b.id = p.child_id
ORDER BY
    a.official_name,
    b.official_name
""")

rows = cur.fetchall()

print("PEDIGREE_EDGES =", len(rows))

for r in rows:
    print(r)

conn.close()
