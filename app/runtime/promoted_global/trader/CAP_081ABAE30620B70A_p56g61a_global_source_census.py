import os,json,psycopg2,re,collections
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G61A_GLOBAL_BUCKING_GENETICS_SOURCE_CENSUS"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

GENETIC_TERMS=[
 "abbi","sire","dam","grandsire","granddam","pedigree",
 "son of","daughter of","offspring","progeny","calf","calves",
 "production sire","production dam","embryo","semen",
 "lot","auction","sale","sold","breeding rights"
]

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

cur.execute("""
select id,source_url,source_type,title,confidence_score,validation_status,raw_payload
from p55a_sources
""")
rows=cur.fetchall()

signals=[]
domains=collections.Counter()
term_counts=collections.Counter()
source_type_counts=collections.Counter()

for r in rows:
    sid,url,stype,title,conf,status,payload=r
    blob=" ".join([
        str(url or ""),
        str(stype or ""),
        str(title or ""),
        json.dumps(payload,ensure_ascii=False,default=str) if payload else ""
    ]).lower()

    hits=[t for t in GENETIC_TERMS if t in blob]

    if url:
        domain=re.sub(r"^www\.","",re.sub(r"^https?://","",url).split("/")[0].lower())
        domains[domain]+=1

    source_type_counts[str(stype)]+=1

    for h in hits:
        term_counts[h]+=1

    if hits:
        signals.append({
          "source_id":str(sid),
          "source_url":url,
          "source_type":stype,
          "title":title,
          "confidence_score":str(conf),
          "validation_status":status,
          "hits":hits,
          "hit_count":len(hits)
        })

signals.sort(key=lambda x:(x["hit_count"],float(x["confidence_score"] or 0)),reverse=True)

report={
 "mission":MISSION,
 "mode":"GLOBAL_CENSUS_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "summary":{
   "total_sources":len(rows),
   "sources_with_genetic_signals":len(signals),
   "top_domains":domains.most_common(30),
   "source_types":source_type_counts.most_common(30),
   "term_counts":term_counts.most_common()
 },
 "top_signal_sources":signals[:300],
 "status":"PASS"
}

(out/"P56G61A_GLOBAL_SOURCE_CENSUS.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps({
 "total_sources":len(rows),
 "sources_with_genetic_signals":len(signals),
 "top_domains":domains.most_common(10),
 "top_terms":term_counts.most_common(15)
},indent=2,ensure_ascii=False))

print("OUTPUT =",out)

cur.close()
conn.close()
