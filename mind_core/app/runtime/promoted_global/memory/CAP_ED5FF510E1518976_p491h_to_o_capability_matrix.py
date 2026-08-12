import json, re, hashlib, csv
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91H_TO_O_PARALLEL_CAPABILITY_MATRIX"
INV=Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P4.91F4_MIND_ONLY_LOCKED_WALK_20260622_125928")
ROOT=Path(r"_evidence\P4.91H_TO_O_PARALLEL_CAPABILITY_MATRIX_20260623_092058")
ITEMS=INV/"exports"/"mind_items.jsonl"

OUT=ROOT/"exports"
LEDGER=ROOT/"ledger"/"processed_ledger.jsonl"
MATRIX=ROOT/"reports"/"capability_matrix.csv"
IDEAS=ROOT/"reports"/"ideas_extracted.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91H_TO_O_CERTIFICATION.txt"

CATEGORIES=[
 "MEMORY","RETRIEVAL","VECTOR","AGENT","RUNTIME","ORCHESTRATION",
 "DATASET","ETL","FINANCE","MARKETING","TRADING","WHATSAPP",
 "ELDORA","MIND","ARCHIVE","OBSOLETE","CODE","DOC","ZIP_SKIPPED"
]

KEYWORDS={
 "MEMORY":["memory","memoria","long_term","short_memory","social_memory","relationship","context_recovery"],
 "RETRIEVAL":["retrieval","rag","search","busca","consulta"],
 "VECTOR":["vector","pgvector","embedding","semantic","semantico"],
 "AGENT":["agent","agente","swarm","planner","governor","task"],
 "RUNTIME":["runtime","worker","service","fastapi","server","orchestrator"],
 "ORCHESTRATION":["pipeline","workflow","orchestrator","queue","scheduler"],
 "DATASET":["dataset","csv","xlsx","parquet","sqlite","db"],
 "ETL":["etl","ingest","import","export","sync"],
 "FINANCE":["trader","trading","ftmo","mt5","profit","order","broker"],
 "MARKETING":["marketing","campanha","criativo","vsl","funil","tiktok","instagram"],
 "WHATSAPP":["whatsapp","twilio","webhook","message","sender"],
 "ELDORA":["eldora"],
 "MIND":["mind","neura","canon"],
 "ARCHIVE":["backup","snapshot","historico","quarentena","duplicados","archive"],
 "OBSOLETE":["old","obsolete","deprecated","legacy","legado"],
 "CODE":[".py",".ps1",".js",".ts",".tsx",".jsx",".sql",".mq5",".mq4",".yml",".yaml",".json",".dockerfile"],
 "DOC":[".md",".txt",".doc",".docx",".pdf",".rtf"]
}

IDEA_PATTERNS=[
 "engine","runtime","memory","retrieval","rag","vector","agent","orchestrator",
 "pipeline","whatsapp","twilio","semantic","graph","ledger","audit","validator",
 "classifier","extractor","recovery","router","governor","planner","dashboard",
 "score","matrix","canary","gate","identity","context","knowledge","supabase",
 "pgvector","fastapi","trading","ftmo","eldora","mind"
]

def now():
    return datetime.now(timezone.utc).isoformat()

def load_jsonl(path):
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    yield json.loads(line)
                except:
                    pass

def key_for(item):
    base=f"{item.get('id','')}|{item.get('path','')}|{item.get('size','')}"
    return hashlib.sha256(base.encode("utf-8","ignore")).hexdigest()

def classify(path, kind):
    p=path.lower()
    cats=set()
    if kind == "ZIP":
        cats.add("ZIP_SKIPPED")
    for cat, keys in KEYWORDS.items():
        for k in keys:
            if k.lower() in p:
                cats.add(cat)
    if not cats:
        cats.add("ARCHIVE" if any(x in p for x in ["backup","snapshot","quarentena","duplicado"]) else "DOC")
    return sorted(cats)

def score(path, cats, kind):
    p=path.lower()
    s=0
    if "ZIP_SKIPPED" in cats:
        return 0
    if any(c in cats for c in ["MEMORY","RETRIEVAL","VECTOR","RUNTIME","AGENT"]): s += 3
    if any(c in cats for c in ["ELDORA","MIND","WHATSAPP","ORCHESTRATION"]): s += 2
    if any(c in cats for c in ["CODE","DATASET","ETL","TRADING","MARKETING"]): s += 1
    if any(x in p for x in ["certified","validated","final","live","operational","production"]): s += 1
    if any(x in p for x in ["quarentena","duplicados","backup","legacy","legado","old","obsolete","deprecated"]): s -= 1
    return max(0,min(5,s))

def status_flags(path, cats, sc):
    p=path.lower()
    flags=[]
    if "ZIP_SKIPPED" in cats: flags.append("ZIP_PENDING_NOT_PROCESSED")
    if any(x in p for x in ["incomplete","partial","pending","todo","fix","hotfix","retry","abort","fail"]):
        flags.append("INCOMPLETE_OR_NEEDS_REVIEW")
    if any(x in p for x in ["old","legacy","legado","deprecated","obsolete"]):
        flags.append("OUTDATED_VERSION")
    if any(x in p for x in ["duplicado","duplicados","copy","copia","backup","snapshot"]):
        flags.append("DUPLICATE_OR_SNAPSHOT")
    if sc >= 4:
        flags.append("HIGH_VALUE_REVIEW")
    if not flags:
        flags.append("OK_CANDIDATE")
    return "|".join(flags)

def extract_ideas(path):
    raw=Path(path).stem.replace("_"," ").replace("-"," ")
    words=[w for w in re.split(r"[^A-Za-z0-9À-ÿ]+", raw) if len(w) >= 3]
    ideas=[]
    low=raw.lower()
    for pat in IDEA_PATTERNS:
        if pat in low:
            ideas.append(pat.upper())
    if len(words) >= 2:
        ideas.append(" ".join(words[:8]).upper())
    return sorted(set(ideas))[:10]

def code_score(path, kind):
    p=path.lower()
    if kind == "ZIP":
        return 0
    if any(p.endswith(ext) for ext in [".py",".ps1",".js",".ts",".tsx",".jsx",".sql",".mq5",".mq4"]):
        return 5
    if any(x in p for x in ["fastapi","runtime","service","worker","router","engine","agent","pipeline"]):
        return 4
    if any(p.endswith(ext) for ext in [".json",".yaml",".yml",".toml",".ini",".env"]):
        return 3
    return 0

def code_exists(path, kind):
    return code_score(path, kind) > 0

seen=set()
rows=[]
idea_rows=[]
processed=0
skipped_zip=0
duplicates=0

for item in load_jsonl(ITEMS):
    if item.get("is_dir"):
        continue

    path=item.get("path","")
    kind=item.get("kind","")
    k=key_for(item)

    if k in seen:
        duplicates += 1
        continue
    seen.add(k)

    cats=classify(path, kind)
    sc=score(path, cats, kind)
    cscore=code_score(path, kind)
    cexists=cscore > 0
    flags=status_flags(path, cats, sc)
    ideas=extract_ideas(path)

    if "ZIP_SKIPPED" in cats:
        skipped_zip += 1

    rec={
        "processed_key":k,
        "drive_id":item.get("id"),
        "path":path,
        "name":item.get("name"),
        "kind":kind,
        "size":item.get("size"),
        "mod_time":item.get("mod_time"),
        "categories":"|".join(cats),
        "score":sc,
        "code_exists":cexists,
        "code_score":cscore,
        "ideas":"|".join(ideas),
        "status_flags":flags,
        "processing_status":"ZIP_SKIPPED" if "ZIP_SKIPPED" in cats else "PROCESSED_METADATA_ONLY",
        "content_opened":False,
        "original_modified":False,
        "reprocess_required":False,
        "certified_at":now()
    }

    rows.append(rec)

    for idea in ideas:
        idea_rows.append({
            "idea":idea,
            "source_path":path,
            "categories":"|".join(cats),
            "score":sc,
            "code_exists":cexists,
            "code_score":cscore,
            "status_flags":flags
        })

    with open(LEDGER,"a",encoding="utf-8") as f:
        f.write(json.dumps(rec,ensure_ascii=True)+"\n")

    processed += 1

fields=list(rows[0].keys()) if rows else []
with open(MATRIX,"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

idea_fields=["idea","source_path","categories","score","code_exists","code_score","status_flags"]
with open(IDEAS,"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=idea_fields)
    w.writeheader()
    w.writerows(idea_rows)

by_score={str(i):0 for i in range(6)}
by_cat={c:0 for c in CATEGORIES}
code_count=0
high_value=0
incomplete=0
outdated=0

for r in rows:
    by_score[str(r["score"])] += 1
    if r["code_exists"]: code_count += 1
    if r["score"] >= 4: high_value += 1
    if "INCOMPLETE_OR_NEEDS_REVIEW" in r["status_flags"]: incomplete += 1
    if "OUTDATED_VERSION" in r["status_flags"]: outdated += 1
    for c in r["categories"].split("|"):
        by_cat[c]=by_cat.get(c,0)+1

summary={
    "mission":MISSION,
    "timestamp":now(),
    "input_inventory":str(ITEMS),
    "files_processed_once":processed,
    "duplicates_skipped":duplicates,
    "zip_skipped_not_extracted":skipped_zip,
    "ideas_extracted":len(idea_rows),
    "code_candidates":code_count,
    "high_value_score_4_5":high_value,
    "incomplete_or_needs_review":incomplete,
    "outdated_version":outdated,
    "by_score":by_score,
    "by_category":by_cat,
    "matrix_csv":str(MATRIX),
    "ideas_csv":str(IDEAS),
    "ledger":str(LEDGER),
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "certification":"CAPABILITY_MATRIX_METADATA_ONLY_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(
    "P4.91H_TO_O COMPLETE\n"
    "CAPABILITY DISCOVERY + CLASSIFICATION + IDEA MATRIX EXECUTED\n"
    "ZIP_EXTRACTION=SKIPPED\n"
    "PROCESS_ONCE=TRUE\n"
    "LEDGER_REQUIRED=TRUE\n"
    "ORIGINAL_MODIFIED=FALSE\n"
    f"FILES_PROCESSED_ONCE={processed}\n"
    f"IDEAS_EXTRACTED={len(idea_rows)}\n"
    f"CODE_CANDIDATES={code_count}\n"
    f"HIGH_VALUE_SCORE_4_5={high_value}\n"
    f"INCOMPLETE_OR_NEEDS_REVIEW={incomplete}\n"
    f"OUTDATED_VERSION={outdated}\n"
    f"MATRIX={MATRIX}\n"
    f"IDEAS={IDEAS}\n"
    f"LEDGER={LEDGER}\n"
    "CERTIFICATION=CAPABILITY_MATRIX_METADATA_ONLY_CERTIFIED\n",
    encoding="utf-8"
)

print(json.dumps(summary,indent=2,ensure_ascii=True))
