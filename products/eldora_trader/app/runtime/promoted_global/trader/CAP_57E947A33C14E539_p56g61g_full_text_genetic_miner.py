import json,re
from pathlib import Path
from datetime import datetime,timezone

MISSION="P5.6G61G_FULL_TEXT_GENETIC_MINER"
base=Path("reports/P5.6G61F_FETCH_HIGH_QUALITY_FULL_TEXT")
txt_dir=base/"txt"
meta=json.loads((base/"P56G61F_FETCH_HIGH_QUALITY_FULL_TEXT.json").read_text(encoding="utf-8"))

out=Path(f"reports/{MISSION}")
out.mkdir(parents=True,exist_ok=True)

entities={}
relations=[]
valuations=[]

def clean(x):
    return re.sub(r"\s+"," ",x or "").strip()

for rec in meta["results"]:
    txt_file=rec.get("txt_file")
    if not txt_file or not Path(txt_file).exists():
        continue

    text=Path(txt_file).read_text(encoding="utf-8",errors="ignore")
    blob=clean(text)
    low=blob.lower()

    abbis=re.findall(r"(?:ABBI#?|Animal ABBI#)\s*[:#]?\s*(\d{2,9})",blob,re.I)
    money=re.findall(r"\$\s?[0-9][0-9,]*(?:\.\d+)?",blob)
    lots=re.findall(r"\bLot\s?#?\s?[A-Za-z0-9\-]+",blob,re.I)

    # Animal ABBI profile
    m=re.search(r"Animal Pedigree\s+(.+?)\s+Animal\s+ABBI#\s+(\d+)",blob,re.I)
    if m:
        name=clean(m.group(1))
        abbi=clean(m.group(2))
        entities[abbi]={
          "official_name":name,
          "registry_number":abbi,
          "source_url":rec.get("source_url"),
          "source_id":rec.get("source_id"),
          "confidence_score":90,
          "status":"ABBI_PROFILE_ENTITY"
        }

    # Generic ABBI candidates from full text
    for a in abbis:
        entities.setdefault(a,{
          "official_name":None,
          "registry_number":a,
          "source_url":rec.get("source_url"),
          "source_id":rec.get("source_id"),
          "confidence_score":70,
          "status":"ABBI_NUMBER_ENTITY_CANDIDATE"
        })

    # SIRE/DAM commercial catalog pattern
    for m in re.finditer(r"SIRE:\s*(.+?)\s+ABBI\s*#?\s*(\d+)\s+DAM:\s*(.+?)\s+ABBI#?\s*(\d+)",blob,re.I):
        sire=clean(m.group(1))
        sire_abbi=clean(m.group(2))
        dam=clean(m.group(3))
        dam_abbi=clean(m.group(4))

        entities[sire_abbi]={
          "official_name":sire,
          "registry_number":sire_abbi,
          "source_url":rec.get("source_url"),
          "source_id":rec.get("source_id"),
          "confidence_score":85,
          "status":"CATALOG_SIRE_ENTITY"
        }
        entities[dam_abbi]={
          "official_name":dam,
          "registry_number":dam_abbi,
          "source_url":rec.get("source_url"),
          "source_id":rec.get("source_id"),
          "confidence_score":80,
          "status":"CATALOG_DAM_ENTITY"
        }

        relations.append({
          "parent":sire,
          "parent_abbi":sire_abbi,
          "child":dam,
          "child_abbi":dam_abbi,
          "relation":"catalog_pair_context",
          "source_url":rec.get("source_url"),
          "source_id":rec.get("source_id"),
          "confidence_score":60,
          "status":"REVIEW_CONTEXT_NOT_PEDIGREE_EDGE"
        })

    # daughter of / son of / sired by
    patterns=[
      ("son of","sire",r"([A-Za-z0-9#' \-\.]{2,80})\s+(?:is\s+)?(?:a\s+)?son of\s+([A-Za-z0-9#' \-\.]{2,80})"),
      ("daughter of","parent_context",r"([A-Za-z0-9#' \-\.]{2,80})\s+(?:is\s+)?(?:a\s+)?daughter of\s+([A-Za-z0-9#' \-\.]{2,80})"),
      ("sired by","sire",r"([A-Za-z0-9#' \-\.]{2,80})\s+(?:is\s+)?sired by\s+([A-Za-z0-9#' \-\.]{2,80})")
    ]

    for phrase,rel,pat in patterns:
        for a,b in re.findall(pat,blob,re.I):
            relations.append({
              "child":clean(a),
              "parent":clean(b),
              "relation":rel,
              "evidence_phrase":phrase,
              "source_url":rec.get("source_url"),
              "source_id":rec.get("source_id"),
              "confidence_score":65 if phrase!="sired by" else 75,
              "status":"TEXT_RELATION_CANDIDATE"
            })

    if money or lots or any(x in low for x in ["semen","embryo","auction","sale","sold"]):
        valuations.append({
          "source_url":rec.get("source_url"),
          "source_id":rec.get("source_id"),
          "title":rec.get("title"),
          "money":money[:20],
          "lots":lots[:20],
          "has_semen":"semen" in low,
          "has_embryo":"embryo" in low,
          "has_sale":any(x in low for x in ["auction","sale","sold"]),
          "status":"FULL_TEXT_VALUATION_CANDIDATE"
        })

report={
 "mission":MISSION,
 "mode":"FULL_TEXT_MINING_NO_DATABASE_WRITE",
 "generated_at":datetime.now(timezone.utc).isoformat(),
 "summary":{
   "txt_files_processed":len(list(txt_dir.glob('*.txt'))),
   "entity_candidates":len(entities),
   "relation_candidates":len(relations),
   "valuation_candidates":len(valuations)
 },
 "entity_candidates":list(entities.values()),
 "relation_candidates":relations[:2000],
 "valuation_candidates":valuations[:1000],
 "status":"PASS"
}

(out/"P56G61G_FULL_TEXT_GENETIC_MINER.json").write_text(
 json.dumps(report,indent=2,ensure_ascii=False),
 encoding="utf-8"
)

print(json.dumps(report["summary"],indent=2,ensure_ascii=False))
print("OUTPUT =",out)
