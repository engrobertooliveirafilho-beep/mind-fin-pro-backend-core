import os
import psycopg2

conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
cur = conn.cursor()

cur.execute("""
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name='p55a_reproduction_records'
ORDER BY ordinal_position
""")

print("REPRODUCTION_SCHEMA")
for r in cur.fetchall():
    print(r)

print("\nREPRODUCTION_RECORDS")
cur.execute("SELECT * FROM p55a_reproduction_records ORDER BY created_at")
for r in cur.fetchall():
    print(r)

conn.close()
