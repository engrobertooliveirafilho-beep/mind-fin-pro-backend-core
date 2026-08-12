import os
import psycopg2

conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
cur = conn.cursor()

print("=== ACTIVE COUNTS ===")
for t in ["p55a_animals","p55a_pedigree_edges","p55a_valuation_events","p55a_reproduction_records"]:
    cur.execute(f"SELECT COUNT(*) FROM {t} WHERE validation_status <> 'quarantined'")
    print(t, cur.fetchone()[0])

print("\n=== ACTIVE PEDIGREE EDGES ===")
cur.execute("""
SELECT a.official_name, p.relation, b.official_name, p.confidence_score, p.validation_status
FROM p55a_pedigree_edges p
JOIN p55a_animals a ON a.id=p.parent_id
JOIN p55a_animals b ON b.id=p.child_id
WHERE p.validation_status <> 'quarantined'
ORDER BY a.official_name,b.official_name
""")

for r in cur.fetchall():
    print(r)

print("\n=== ACTIVE ANIMALS ===")
cur.execute("""
SELECT official_name, confidence_score, validation_status
FROM p55a_animals
WHERE validation_status <> 'quarantined'
ORDER BY official_name
""")

for r in cur.fetchall():
    print(r)

conn.close()
