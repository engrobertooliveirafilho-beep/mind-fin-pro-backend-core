import os, psycopg2

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

cur.execute("""
SELECT a.official_name,p.relation,b.official_name,p.confidence_score,p.validation_status,p.created_at
FROM p55a_pedigree_edges p
JOIN p55a_animals a ON a.id=p.parent_id
JOIN p55a_animals b ON b.id=p.child_id
WHERE p.validation_status <> 'quarantined'
ORDER BY p.created_at DESC
LIMIT 30
""")

for r in cur.fetchall():
    print(r)

conn.close()
