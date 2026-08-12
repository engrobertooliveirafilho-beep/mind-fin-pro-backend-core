import os
import psycopg2
import collections
import urllib.parse
import json
from pathlib import Path

out = Path(os.environ.get("G26OUT", "."))
out.mkdir(parents=True, exist_ok=True)

conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
cur = conn.cursor()

cur.execute("""
select column_name, data_type
from information_schema.columns
where table_name='p55a_sources'
order by ordinal_position
""")
columns = cur.fetchall()

print("COLUMNS")
for c in columns:
    print(c)

colnames = [c[0] for c in columns]

url_col = "source_url" if "source_url" in colnames else None
type_col = "source_type" if "source_type" in colnames else None
confidence_col = "confidence_score" if "confidence_score" in colnames else None
status_col = "validation_status" if "validation_status" in colnames else None

select_cols = [x for x in [url_col, type_col, confidence_col, status_col] if x]
cur.execute("select " + ",".join(select_cols) + " from p55a_sources")
rows = cur.fetchall()

domains = collections.Counter()
types = collections.Counter()
statuses = collections.Counter()
real = 0
empty = 0

idx = {name:i for i,name in enumerate(select_cols)}

for r in rows:
    source_url = r[idx[url_col]] if url_col else None
    source_type = r[idx[type_col]] if type_col else None
    confidence = r[idx[confidence_col]] if confidence_col else None
    status = r[idx[status_col]] if status_col else None

    if source_url:
        real += 1
        domains[urllib.parse.urlparse(source_url).netloc.lower()] += 1
    else:
        empty += 1

    types[str(source_type)] += 1
    statuses[str(status)] += 1

summary = {
    "total": len(rows),
    "real_urls": real,
    "empty_urls": empty,
    "top_domains": domains.most_common(30),
    "source_types": types.most_common(30),
    "statuses": statuses.most_common(30),
    "columns": columns
}

print("\nSUMMARY")
print(json.dumps(summary, indent=2, default=str, ensure_ascii=False))

Path(out / "P56G26C_P55A_SOURCES_AUDIT.json").write_text(
    json.dumps(summary, indent=2, default=str, ensure_ascii=False),
    encoding="utf-8"
)

cur.execute("""
select *
from p55a_sources
where lower(source_url) like '%pbr%'
   or lower(source_url) like '%americanbuckingbull%'
   or lower(source_url) like '%abbi%'
limit 100
""")

matches = cur.fetchall()

print("\nABBI_PBR_MATCHES")
for m in matches:
    print(m)

Path(out / "P56G26C_ABBI_PBR_MATCHES.txt").write_text(
    "\n".join(str(m) for m in matches),
    encoding="utf-8"
)

cur.close()
conn.close()
