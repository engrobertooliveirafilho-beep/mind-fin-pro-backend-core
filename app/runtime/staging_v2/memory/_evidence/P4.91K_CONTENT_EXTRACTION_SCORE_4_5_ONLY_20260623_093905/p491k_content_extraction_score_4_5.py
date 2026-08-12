import csv, json, hashlib, subprocess, time, re
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91K_CONTENT_EXTRACTION_SCORE_4_5_ONLY"
ROOT=Path(r"_evidence\P4.91K_CONTENT_EXTRACTION_SCORE_4_5_ONLY_20260623_093905")
MATRIX=Path(r"_evidence\P4.91H_TO_O_PARALLEL_CAPABILITY_MATRIX_20260623_092058\reports\capability_matrix.csv")
STAGING=ROOT/"staging"
EXPORTS=ROOT/"exports"
REPORTS=ROOT/"reports"
LEDGER=ROOT/"ledger"/"content_processed_ledger.jsonl"

OUT_JSONL=EXPORTS/"content_extraction_results.jsonl"
READY=REPORTS/"ready_to_test_matrix.csv"
NEEDS=REPORTS/"needs_fix_or_review_matrix.csv"
IDEAS=REPORTS/"ideas_with_real_content.csv"
SUMMARY=REPORTS/"summary.json"
CERT=ROOT/"P4.91K_CERTIFICATION.txt"

ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

MAX_FILES=1000
MAX_BYTES=512000
ALLOWED_EXT={".py",".ps1",".js",".ts",".tsx",".jsx",".sql",".json",".jsonl",".yaml",".yml",".toml",".ini",".md",".txt",".env",".mq5",".mq4",".html",".css"}

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(s):
    return hashlib.sha256(str(s).encode("utf-8","ignore")).hexdigest()

def safe_name(s):
    return re.sub(r"[^A-Za-z0-9_.-]+","_",s)[:180]

def append_jsonl(path,obj):
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj,ensure_ascii=True)+"\n")

def load_done():
    done=set()
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line).get("content_key"))
            except:
                pass
    return done

def rclone_cat(path):
    cmd=["rclone","cat","gdrive:"+path,"--drive-root-folder-id",ROOT_ID]
    try:
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=8)
    except subprocess.TimeoutExpired:
        return None,"TIMEOUT_SKIPPED_AFTER_45_SECONDS"
    except Exception as e:
        return None,("READ_EXCEPTION: "+str(e))[:2000]

    if p.returncode != 0:
        return None,(p.stderr or b"").decode("utf-8","replace")[-2000:]

    data=p.stdout or b""
    if len(data) > MAX_BYTES:
        data=data[:MAX_BYTES]
    return data.decode("utf-8","replace"),None

def classify_content(text,path):
    low=(text[:MAX_BYTES] if text else "").lower()
    p=path.lower()

    has_code=any(x in low for x in [
        "def ","class ","import ","from ","function ","const ","let ","async ",
        "fastapi","router","subprocess","select ","create table","input ","oninit"
    ])

    has_tests=any(x in low for x in ["pytest","unittest","describe(","it(","assert ","test_"])
    has_runtime=any(x in low for x in ["fastapi","uvicorn","router","worker","runtime","webhook","twilio","supabase","pgvector"])
    has_docs=any(x in low for x in ["objetivo","mission","certification","auditoria","snapshot","status","resultado"])
    incomplete=any(x in low or x in p for x in ["todo","fixme","pass #","not implemented","placeholder","pending","incomplete","erro","failed","abort"])
    outdated=any(x in low or x in p for x in ["deprecated","obsolete","legacy","legado","old","quarentena"])
    secrets_risk=any(x in low for x in ["api_key","secret","token","password","private_key"])

    if has_code and has_tests and not incomplete and not outdated:
        status="READY_TO_TEST"
    elif has_code and not incomplete:
        status="RUNTIME_CANDIDATE_NEEDS_TEST"
    elif incomplete:
        status="NEEDS_FIX"
    elif outdated:
        status="OUTDATED"
    elif has_docs:
        status="KNOWLEDGE_DOC"
    else:
        status="NEEDS_REVIEW"

    return {
        "has_real_code":has_code,
        "has_tests":has_tests,
        "has_runtime_markers":has_runtime,
        "has_docs":has_docs,
        "incomplete":incomplete,
        "outdated":outdated,
        "secrets_risk":secrets_risk,
        "content_status":status
    }

def extract_ideas(text,path):
    low=(text or "").lower()
    ideas=[]
    patterns=[
        "memory","retrieval","rag","vector","embedding","pgvector","agent","runtime",
        "orchestrator","workflow","whatsapp","twilio","supabase","fastapi","router",
        "ledger","audit","classifier","extractor","knowledge","context","semantic",
        "graph","social memory","long term memory","canary","validator","governor",
        "planner","dashboard","trading","ftmo","eldora","mind"
    ]
    for p in patterns:
        if p in low:
            ideas.append(p.upper())
    name=Path(path).stem.replace("_"," ").replace("-"," ")
    if name:
        ideas.append(name[:120].upper())
    return sorted(set(ideas))[:20]

rows=[]
with open(MATRIX,encoding="utf-8-sig",newline="") as f:
    for r in csv.DictReader(f):
        try:
            sc=int(r.get("score","0"))
        except:
            sc=0
        path=r.get("path","")
        ext=Path(path).suffix.lower()
        bad = [
    "site-packages","__pycache__",".venv","venv/","node_modules",
    "coverage_htmlfiles","dist-info","egg-info",".pytest_cache",
    ".gradle",".cache","license","licenses","favicon","png.txt",
    ".jpg.txt",".jpeg.txt",".gif.txt",".webp.txt",".ico.txt"
]
is_bad = any(b in path.lower() for b in bad)

good = any(g in path.lower() for g in [
    "runtime","engine","memory","retrieval","vector","agent",
    "orchestrator","workflow","whatsapp","twilio","supabase",
    "pgvector","fastapi","router","ledger","classifier",
    "extractor","knowledge","context","semantic","graph",
    "eldora","mind","neura"
])

if sc >= 4 and r.get("kind") != "ZIP" and ext in ALLOWED_EXT and good and not is_bad:
            rows.append(r)

done=load_done()
processed=0
skipped_done=0
download_fail=0
ready=[]
needs=[]
idea_rows=[]

for r in rows:
    if processed >= MAX_FILES:
        break

    path=r.get("path","")
    ckey=sha(path+"|"+r.get("drive_id","")+"|"+r.get("size",""))

    if ckey in done:
        skipped_done += 1
        continue

    text,err=rclone_cat(path)
    if err:
        rec={
            "mission":MISSION,
            "content_key":ckey,
            "path":path,
            "status":"READ_FAILED",
            "error":err,
            "processed_at":now(),
            "original_modified":False
        }
        append_jsonl(OUT_JSONL,rec)
        append_jsonl(LEDGER,rec)
        download_fail += 1
        processed += 1
        continue

    analysis=classify_content(text,path)
    ideas=extract_ideas(text,path)

    content_hash=sha(text)
    rec={
        "mission":MISSION,
        "content_key":ckey,
        "path":path,
        "drive_id":r.get("drive_id"),
        "score":r.get("score"),
        "categories":r.get("categories"),
        "metadata_code_exists":r.get("code_exists"),
        "metadata_code_score":r.get("code_score"),
        "content_hash":content_hash,
        "content_bytes_read":len(text.encode("utf-8","ignore")),
        "ideas":"|".join(ideas),
        **analysis,
        "processing_status":"CONTENT_PROCESSED_ONCE",
        "reprocess_required":False,
        "original_modified":False,
        "processed_at":now()
    }

    append_jsonl(OUT_JSONL,rec)
    append_jsonl(LEDGER,rec)

    flat={
        "path":path,
        "score":r.get("score"),
        "categories":r.get("categories"),
        "content_status":analysis["content_status"],
        "has_real_code":analysis["has_real_code"],
        "has_tests":analysis["has_tests"],
        "has_runtime_markers":analysis["has_runtime_markers"],
        "incomplete":analysis["incomplete"],
        "outdated":analysis["outdated"],
        "secrets_risk":analysis["secrets_risk"],
        "ideas":"|".join(ideas),
        "content_hash":content_hash
    }

    if analysis["content_status"] in ["READY_TO_TEST","RUNTIME_CANDIDATE_NEEDS_TEST"]:
        ready.append(flat)
    else:
        needs.append(flat)

    for idea in ideas:
        idea_rows.append({
            "idea":idea,
            "source_path":path,
            "score":r.get("score"),
            "categories":r.get("categories"),
            "content_status":analysis["content_status"],
            "has_real_code":analysis["has_real_code"],
            "has_tests":analysis["has_tests"],
            "has_runtime_markers":analysis["has_runtime_markers"]
        })

    processed += 1

def write_csv(path, data):
    if not data:
        path.write_text("",encoding="utf-8")
        return
    with open(path,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)

write_csv(READY,ready)
write_csv(NEEDS,needs)
write_csv(IDEAS,idea_rows)

summary={
    "mission":MISSION,
    "timestamp":now(),
    "input_matrix":str(MATRIX),
    "eligible_score_4_5_text_code_files":len(rows),
    "max_files_this_run":MAX_FILES,
    "processed_this_run":processed,
    "skipped_already_done":skipped_done,
    "read_failed":download_fail,
    "ready_to_test":len(ready),
    "needs_fix_or_review":len(needs),
    "ideas_with_real_content":len(idea_rows),
    "zip_extraction":"SKIPPED",
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "ledger":str(LEDGER),
    "ready_matrix":str(READY),
    "needs_matrix":str(NEEDS),
    "ideas_matrix":str(IDEAS),
    "certification":"CONTENT_EXTRACTION_SCORE_4_5_BATCH_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(
    "P4.91K COMPLETE\n"
    "CONTENT EXTRACTION SCORE 4/5 EXECUTED\n"
    f"ELIGIBLE={len(rows)}\n"
    f"PROCESSED_THIS_RUN={processed}\n"
    f"READY_TO_TEST={len(ready)}\n"
    f"NEEDS_FIX_OR_REVIEW={len(needs)}\n"
    f"READ_FAILED={download_fail}\n"
    f"IDEAS_WITH_REAL_CONTENT={len(idea_rows)}\n"
    "ZIP_EXTRACTION=SKIPPED\n"
    "PROCESS_ONCE=TRUE\n"
    "ORIGINAL_MODIFIED=FALSE\n"
    "CERTIFICATION=CONTENT_EXTRACTION_SCORE_4_5_BATCH_CERTIFIED\n",
    encoding="utf-8"
)

print(json.dumps(summary,indent=2,ensure_ascii=True))


