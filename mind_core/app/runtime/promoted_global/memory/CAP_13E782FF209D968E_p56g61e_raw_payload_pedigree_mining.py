import os,json,re,psycopg2
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G61E_RAW_PAYLOAD_PEDIGREE_MINING"
out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

src=Path("reports/P5.6G61B_GLOBAL_HIGH_QUALITY_SOURCE_FILTER/P56G61B_GLOBAL_HIGH_QUALITY_SOURCE_FILTER.json")
data=json.loads(src.read_text(encoding="utf-8"))

conn=psycopg2.connect(os.getenv("DATABASE_URL"),sslmode="require")
cur=conn.cursor()

results=[]
entity_candidates={}
relation_candidates=[]
valuation_candidates=[]

def clean(x):
    return re.sub(r"\s+"," ",str(x or "")).strip()

for s in data["high_quality_sources"]:
    sid=s["source_id"]

    cur.execute("""
    select id,source_url,source_type,title,confidence_score,validation_status,raw_payload
    from p55a_sources
    where id=%s
    """,(sid,))
    row=cur.fetchone()
    if not row:
        continue

    source_id,source_url,source_type,title,conf,status,raw_payload=row

    blob=clean(" ".join([
      str(title or ""),
      str(source_url or ""),
      json.dumps(raw_payload,ensure_ascii=False,default=str) if raw_payload else ""
    ]))

    abbis=re.findall(r"(?:ABBI#?|Animal ABBI#)\s*[:#]?\s*(\d{2,9})",blob,re.I)
    money=re.findall(r"\$\s?[0-9][0-9,]*(?:\.\d+)?",blob)
    lots=re.findall(r"\bLot\s?#?\s?[A-Za-z0-9\-]+",blob,re.I)

    # Captura títulos comerciais tipo "Red Wolf DAM: Bodacious Daughter Lot #2280"
    title_patterns=[]
    m=re.search(r"(.+?)\s+DAM:\s+(.+?)(?:\s+Lot|\s+-|$)",str(title or ""),re.I)
    if m:
        animal=clean(m.group(1))
        dam=clean(m.group(2))
        title_patterns.append({"animal":animal,"dam":dam,"pattern":"TITLE_ANIMAL_DAM"})

    m2=re.search(r"SIRE:\s+(.+?)\s+DAM:\s+(.+?)(?:\s+Lot|\s+-|$)",str(title or ""),re.I)
    if m2:
        sire=clean(m2.group(1))
        dam=clean(m2.group(2))
        title_patterns.append({"sire":sire,"dam":dam,"pattern":"TITLE_SIRE_DAM"})

    # Relações textuais diretas
    son_of=re.findall(r"([A-Za-z0-9#' \-\.]+?)\s+(?:is\s+)?(?:a\s+)?son of\s+([A-Za-z0-9#' \-\.]+)",blob,re.I)
    daughter_of=re.findall(r"([A-Za-z0-9#' \-\.]+?)\s+(?:is\s+)?(?:a\s+)?daughter of\s+([A-Za-z0-9#' \-\.]+)",blob,re.I)
    sired_by=re.findall(r"([A-Za-z0-9#' \-\.]+?)\s+(?:is\s+)?sired by\s+([A-Za-z0-9#' \-\.]+)",blob,re.I)

    for a in abbis:
        entity_candidates[a]={
          "registry_number":a,
          "source_id":str(source_id),
          "source_url":source_url,
          "confidence_score":75,
          "status":"ABBI_FOUND_IN_RAW_PAYLOAD"
        }

    for child,parent in son_of:
        relation_candidates.append({
          "child":clean(child),
          "parent":clean(parent),
          "relation":"sire",
          "evidence_phrase":"son of",
          "source_id":str(source_id),
          "source_url":source_url,
          "confidence_score":65,
          "status":"TEXT_RELATION_CANDIDATE"
        })

    for child,parent in daughter_of:
        relation_candidates.append({
          "child":clean(child),
          "parent":clean(parent),
          "relation":"dam_or_sire_context",
          "evidence_phrase":"daughter of",
          "source_id":str(source_id),
          "source_url":source_url,
          "confidence_score":60,
          "status":"TEXT_RELATION_CANDIDATE_REVIEW"
        })

    for child,parent in sired_by:
        relation_candidates.append({
          "child":clean(child),
          "parent":clean(parent),
          "relation":"sire",
          "evidence_phrase":"sired by",
          "source_id":str(source_id),
          "source_url":source_url,
          "confidence_score":70,
          "status":"TEXT_RELATION_CANDIDATE"
        })

    for p in title_patterns:
        relation_candidates.append({
          **p,
          "source_id":str(source_id),
          "source_url":source_url,
          "confidence_score":70,
          "status":"TITLE_RELATION_CANDIDATE"
        })

    if money or lots or any(x in blob.lower() for x in ["semen","embryo","auction","sale","sold"]):
        valuation_candidates.append({
          "source_id":str(source_id),
          "source_url":source_url,
          "title":title,
          "money":money,
          "lots":lots,
          "has_semen":"semen" in blob.lower(),
          "has_embryo":"embryo" in blob.lower(),
          "has_sale":"sale" in blob.lower() or "sold" in blob.lower() or "auction" in blob.lower(),
          "confidence_score":70,
          "status":"RAW_VALUATION_CANDIDATE"
        })

    results.append({
      "source_id":str(source_id),
      "source_url":source_url,
      "title":title,
      "abbi_count":len(abbis),
      "money_count":len(money),
      "lot_count":len(lots),
      "son_of_count":len(son_of),
      "daughter_of_count":len(daughter_of),
      "sired_by_count":len(sired_by),
      "title_patterns":title_patterns
    })

report={
 "mission":MISSION,
 "mode":"RAW_PAYLOAD_MINING_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "summary":{
   "sources_processed":len(results),
   "entity_candidates":len(entity_candidates),
   "relation_candidates":len(relation_candidates),
   "valuation_candidates":len(valuation_candidates),
   "sources_with_abbi":sum(1 for r in results if r["abbi_count"]>0),
   "sources_with_relations":sum(1 for r in results if r["son_of_count"]+r["daughter_of_count"]+r["sired_by_count"]+len(r["title_patterns"])>0)
 },
 "source_results":results,
 "entity_candidates":list(entity_candidates.values()),
 "relation_candidates":relation_candidates,
 "valuation_candidates":valuation_candidates,
 "status":"PASS"
}

(out/"P56G61E_RAW_PAYLOAD_PEDIGREE_MINING.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False,default=str),
 encoding="utf-8"
)

print(json.dumps(report["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =",out)

cur.close()
conn.close()
