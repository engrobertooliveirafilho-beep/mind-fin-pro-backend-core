import os, psycopg2

conn=psycopg2.connect(os.environ["DATABASE_URL"],sslmode="require")
cur=conn.cursor()

cur.execute("""
SELECT
  p.id,
  parent.official_name,
  parent.confidence_score,
  parent.validation_status,
  p.relation,
  child.id,
  child.official_name,
  child.confidence_score,
  child.validation_status,
  p.created_at
FROM p55a_pedigree_edges p
JOIN p55a_animals parent ON parent.id=p.parent_id
JOIN p55a_animals child ON child.id=p.child_id
WHERE parent.official_name='Whitewater Skoal'
AND child.official_name='Bushwacker'
AND p.validation_status <> 'quarantined'
ORDER BY child.confidence_score DESC, p.created_at ASC
""")

for r in cur.fetchall():
    print(r)

conn.close()
