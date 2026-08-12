import os
import psycopg2

conn = psycopg2.connect(
    os.environ["DATABASE_URL"],
    sslmode="require"
)

cur = conn.cursor()

cur.execute("""
SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name='p55a_pedigree_edges'
ORDER BY ordinal_position
""")

cols = cur.fetchall()

print("COLUMNS:")
for c in cols:
    print(c)

conn.close()
