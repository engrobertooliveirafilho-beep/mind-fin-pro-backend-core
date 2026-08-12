import os,json,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G61H_GLOBAL_CANDIDATE_RECONCILIATION"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

src=Path("reports/P5.6G61G_FULL_TEXT_GENETIC_MINER/P56G61G_FULL_TEXT_GENETIC_MINER.json")
data=json.loads(src.read_text(encoding="utf-8"))

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

existing=[]
new=[]
weak=[]

for e in data["entity_candidates"]:
    reg=e.get("registry_number")
    if not reg:
        weak.append(e)
        continue

    cur.execute("""
    select id,official_name,registry_number,confidence_score,validation_status
    from p55a_animals
    where registry_number=%s
    limit 1
    """,(reg,))
    row=cur.fetchone()

    if row:
        existing.append({
          **e,
          "existing_id":str(row[0]),
          "existing_name":row[1],
          "existing_status":row[4]
        })
    else:
        if e.get("official_name"):
            new.append(e)
        else:
            weak.append(e)

promotable_relations=[]
review_relations=[]
context_relations=[]

for r in data["relation_candidates"]:
    if r.get("status")=="REVIEW_CONTEXT_NOT_PEDIGREE_EDGE":
        context_relations.append(r)
    elif r.get("confidence_score",0) >= 70 and r.get("parent") and r.get("child"):
        promotable_relations.append(r)
    else:
        review_relations.append(r)

report={
 "mission":MISSION,
 "mode":"RECONCILE_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "summary":{
   "entity_candidates":len(data["entity_candidates"]),
   "existing_entities":len(existing),
   "new_named_entities":len(new),
   "weak_or_registry_only":len(weak),
   "relation_candidates":len(data["relation_candidates"]),
   "promotable_relation_review":len(promotable_relations),
   "review_relations":len(review_relations),
   "context_relations":len(context_relations),
   "valuation_candidates":len(data["valuation_candidates"])
 },
 "existing_entities":existing[:500],
 "new_named_entities":new[:500],
 "weak_or_registry_only":weak[:500],
 "promotable_relation_review":promotable_relations[:500],
 "review_relations":review_relations[:500],
 "context_relations":context_relations[:500],
 "valuation_candidates":data["valuation_candidates"][:500],
 "status":"PASS"
}

(out/"P56G61H_GLOBAL_CANDIDATE_RECONCILIATION.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =",out)

cur.close()
conn.close()
