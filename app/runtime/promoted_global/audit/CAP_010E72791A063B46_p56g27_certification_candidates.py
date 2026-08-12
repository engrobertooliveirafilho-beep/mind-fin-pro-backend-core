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
select
    source_url,
    source_type,
    title,
    confidence_score,
    validation_status
from p55a_sources
where validation_status='provisional'
""")

rows = cur.fetchall()

domains = {
    "ABBI": [],
    "PBR": [],
    "SALE": [],
    "SEMEN": [],
    "EMBRYO": [],
    "BREEDER": []
}

for r in rows:

    url = (r[0] or "").lower()

    if "americanbuckingbull" in url:
        domains["ABBI"].append(r)

    elif "pbr.com" in url:
        domains["PBR"].append(r)

    elif any(x in url for x in [
        "sale",
        "auction",
        "sirebuyer",
        "nextlot",
        "givesmart"
    ]):
        domains["SALE"].append(r)

    elif any(x in url for x in [
        "semen",
        "stud"
    ]):
        domains["SEMEN"].append(r)

    elif "embryo" in url:
        domains["EMBRYO"].append(r)

    elif any(x in url for x in [
        "breeder",
        "ranch",
        "genetics"
    ]):
        domains["BREEDER"].append(r)

out = Path("reports/P5.6G27_STRUCTURED_SOURCE_CERTIFICATION")
out.mkdir(parents=True, exist_ok=True)

summary = {}

for k,v in domains.items():
    summary[k] = len(v)

    with open(
        out / f"{k.lower()}_candidates.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(v,f,indent=2,default=str)

print(json.dumps(summary,indent=2))

with open(
    out / "P56G27_CERTIFICATION_SUMMARY.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(summary,f,indent=2)

cur.close()
conn.close()
