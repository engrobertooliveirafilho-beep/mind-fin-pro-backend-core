import os,json,uuid,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G53_REGISTER_LOCAL_EVIDENCE_AND_BIND_EDGES"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

g39=Path("reports/P5.6G39_ABBI_MAX_GENETIC_EXPANSION_BFS/P56G39_ABBI_MAX_GENETIC_EXPANSION_BFS.json")
g48=Path("reports/P5.6G48_PRIMARY_SOURCE_EXTRACTION_TIER1/P56G48_PRIMARY_SOURCE_EXTRACTION_TIER1.json")

abbi_data=json.loads(g39.read_text(encoding="utf-8"))
tier1_data=json.loads(g48.read_text(encoding="utf-8"))

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

report={
 "mission":MISSION,
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "mode":"DRY_RUN_ROLLBACK_COMMIT_VALIDATE",
 "sources_planned":[],
 "sources_created":[],
 "bindings_planned":[],
 "bindings_committed":[],
 "status":"UNKNOWN"
}

try:
    for p in abbi_data.get("profiles",[]):
        url=p.get("url")
        if not url:
            continue

        cur.execute("""
        select id from p55a_sources
        where source_url=%s
        order by confidence_score desc nulls last
        limit 1
        """,(url,))
        row=cur.fetchone()

        report["sources_planned"].append({
          "source_id":str(row[0]) if row else str(uuid.uuid4()),
          "source_url":url,
          "source_type":"ABBI_LOCAL_HTML",
          "title":f"ABBI profile {p.get('animal')} #{p.get('abbi')}",
          "confidence_score":90,
          "validation_status":"provisional",
          "raw_payload":{
            "mission":MISSION,
            "origin":"G39_LOCAL_HTML",
            "animal":p.get("animal"),
            "abbi":p.get("abbi"),
            "sha256":p.get("sha256")
          },
          "action":"EXISTS" if row else "CREATE"
        })

    for s in tier1_data.get("sources",[]):
        url=s.get("final_url") or s.get("url")
        if not url:
            continue

        cur.execute("""
        select id from p55a_sources
        where source_url=%s
        order by confidence_score desc nulls last
        limit 1
        """,(url,))
        row=cur.fetchone()

        report["sources_planned"].append({
          "source_id":str(row[0]) if row else str(uuid.uuid4()),
          "source_url":url,
          "source_type":"COMMERCIAL_LOCAL_HTML",
          "title":s.get("title"),
          "confidence_score":80,
          "validation_status":"provisional",
          "raw_payload":{
            "mission":MISSION,
            "origin":"G48_LOCAL_HTML",
            "source_id_original":s.get("source_id"),
            "sha256":s.get("sha256"),
            "signals":s.get("signals")
          },
          "action":"EXISTS" if row else "CREATE"
        })

    # rollback source creation
    cur.execute("BEGIN;")
    for s in report["sources_planned"]:
        if s["action"]=="CREATE":
            cur.execute("""
            insert into p55a_sources
            (id,source_url,source_type,title,confidence_score,validation_status,raw_payload)
            values (%s,%s,%s,%s,%s,%s,%s)
            """,(
              s["source_id"],s["source_url"],s["source_type"],s["title"],
              s["confidence_score"],s["validation_status"],json.dumps(s["raw_payload"])
            ))
    conn.rollback()

    # commit source creation
    for s in report["sources_planned"]:
        if s["action"]=="CREATE":
            cur.execute("""
            insert into p55a_sources
            (id,source_url,source_type,title,confidence_score,validation_status,raw_payload)
            values (%s,%s,%s,%s,%s,%s,%s)
            """,(
              s["source_id"],s["source_url"],s["source_type"],s["title"],
              s["confidence_score"],s["validation_status"],json.dumps(s["raw_payload"])
            ))
            report["sources_created"].append(s)
    conn.commit()

    source_by_child_abbi={}
    for s in report["sources_planned"]:
        raw=s["raw_payload"]
        abbi=raw.get("abbi")
        if abbi:
            source_by_child_abbi[str(abbi)]=s["source_id"]

    cur.execute("""
    select
      e.id,
      p.registry_number parent_abbi,
      c.registry_number child_abbi
    from p55a_pedigree_edges e
    left join p55a_animals p on p.id=e.parent_id
    left join p55a_animals c on c.id=e.child_id
    where e.evidence_source_id is null
      and c.registry_number is not null
    """)

    for edge_id,parent_abbi,child_abbi in cur.fetchall():
        source_id=source_by_child_abbi.get(str(child_abbi))
        if source_id:
            report["bindings_planned"].append({
              "edge_id":str(edge_id),
              "parent_abbi":str(parent_abbi),
              "child_abbi":str(child_abbi),
              "source_id":source_id
            })

    # rollback binding
    cur.execute("BEGIN;")
    for b in report["bindings_planned"]:
        cur.execute("""
        update p55a_pedigree_edges
        set evidence_source_id=%s
        where id=%s and evidence_source_id is null
        """,(b["source_id"],b["edge_id"]))
    conn.rollback()

    # commit binding
    for b in report["bindings_planned"]:
        cur.execute("""
        update p55a_pedigree_edges
        set evidence_source_id=%s
        where id=%s and evidence_source_id is null
        """,(b["source_id"],b["edge_id"]))
        report["bindings_committed"].append(b)
    conn.commit()

    report["summary"]={
      "sources_planned":len(report["sources_planned"]),
      "sources_created":len(report["sources_created"]),
      "bindings_planned":len(report["bindings_planned"]),
      "bindings_committed":len(report["bindings_committed"])
    }
    report["status"]="PASS"

except Exception as e:
    conn.rollback()
    report["status"]="FAILED"
    report["error"]=repr(e)

(out/"P56G53_REGISTER_LOCAL_EVIDENCE_AND_BIND_EDGES_REPORT.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report.get("summary",report),indent=2,ensure_ascii=False,default=str))
print("STATUS =",report["status"])

cur.close()
conn.close()
