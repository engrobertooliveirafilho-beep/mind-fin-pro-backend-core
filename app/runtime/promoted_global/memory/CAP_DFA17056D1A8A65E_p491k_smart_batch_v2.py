import csv, json, subprocess, hashlib, re
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91K_CONTENT_EXTRACTION_SMART_BATCH_V2"
ROOT=Path(r"_evidence\P4.91K_CONTENT_EXTRACTION_SMART_BATCH_V2_20260623_115036")
MATRIX=Path(r"_evidence\P4.91H_TO_O_PARALLEL_CAPABILITY_MATRIX_20260623_092058\reports\capability_matrix.csv")
ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

LEDGER=ROOT/"ledger"/"ledger.jsonl"
RESULTS=ROOT/"exports"/"content_results.jsonl"
READY=ROOT/"reports"/"ready_to_test.csv"
NEEDS=ROOT/"reports"/"needs_review.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91K_SMART_BATCH_V2_CERTIFICATION.txt"

MAX_FILES=1000
MAX_BYTES=300000

BAD=[
 "site-packages","__pycache__",".venv","venv/","node_modules",
 "coverage_htmlfiles","dist-info","egg-info",".pytest_cache",
 ".gradle",".cache","license","licenses","favicon",
 ".png",".jpg",".jpeg",".gif",".webp",".ico",".mp3",".mp4",".mov",".zip"
]

GOOD_CATS=[
 "MEMORY","RETRIEVAL","VECTOR","AGENT","RUNTIME","ORCHESTRATION",
 "WHATSAPP","ELDORA","MIND","CODE","ETL"
]

GOOD_EXT=[
 ".py",".ps1",".js",".ts",".tsx",".jsx",".sql",".json",".jsonl",
 ".yaml",".yml",".toml",".ini",".md",".txt",".mq5",".mq4"
]

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(x):
    return hashlib.sha256(str(x).encode("utf-8","ignore")).hexdigest()

def append(path,obj):
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj,ensure_ascii=True)+"\n")

def is_good_row(r):
    path=(r.get("path") or "").lower()
    ext=Path(path).suffix.lower()
    cats=(r.get("categories") or "")
    try:
        sc=int(r.get("score") or 0)
    except:
        sc=0

    if sc < 4:
        return False
    if r.get("kind") == "ZIP":
        return False
    if ext not in GOOD_EXT:
        return False
    if any(b in path for b in BAD):
        return False
    if not any(c in cats for c in GOOD_CATS):
        return False
    return True

def rclone_cat(path):
    cmd=["rclone","cat","gdrive:"+path,"--drive-root-folder-id",ROOT_ID]
    try:
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=10)
    except subprocess.TimeoutExpired:
        return None,"TIMEOUT_10S"
    except Exception as e:
        return None,("EXCEPTION:"+str(e))[:1000]

    if p.returncode != 0:
        return None,(p.stderr or b"").decode("utf-8","replace")[-1000:]

    data=p.stdout or b""
    if len(data)>MAX_BYTES:
        data=data[:MAX_BYTES]
    return data.decode("utf-8","replace"),None

def analyze(text,path):
    low=(text or "").lower()
    p=path.lower()

    has_code=any(x in low for x in [
        "def ","class ","import ","from ","function ","const ","let ",
        "async ","await ","fastapi","router","select ","create table",
        "param(","oninit","input "
    ])
    has_test=any(x in low for x in ["pytest","unittest","assert ","describe(","it(","test_"])
    runtime=any(x in low for x in ["fastapi","uvicorn","router","webhook","twilio","supabase","pgvector","runtime","worker"])
    incomplete=any(x in low or x in p for x in ["todo","fixme","not implemented","placeholder","pending","incomplete","failed","abort"])
    outdated=any(x in low or x in p for x in ["deprecated","obsolete","legacy","legado","old","quarentena"])
    doc=any(x in low for x in ["objetivo","mission","status","certification","auditoria","snapshot","resultado"])

    if has_code and runtime and has_test and not incomplete and not outdated:
        status="READY_TO_TEST"
    elif has_code and runtime and not incomplete:
        status="RUNTIME_CANDIDATE_NEEDS_TEST"
    elif has_code:
        status="CODE_CANDIDATE_REVIEW"
    elif doc:
        status="KNOWLEDGE_DOC"
    elif incomplete:
        status="INCOMPLETE"
    elif outdated:
        status="OUTDATED"
    else:
        status="NEEDS_REVIEW"

    ideas=[]
    for k in ["memory","retrieval","rag","vector","embedding","agent","runtime","orchestrator","workflow","whatsapp","twilio","supabase","fastapi","ledger","classifier","extractor","knowledge","context","semantic","graph","eldora","mind"]:
        if k in low or k in p:
            ideas.append(k.upper())

    return {
        "status":status,
        "has_code":has_code,
        "has_test":has_test,
        "runtime_marker":runtime,
        "incomplete":incomplete,
        "outdated":outdated,
        "ideas":"|".join(sorted(set(ideas))[:20])
    }

rows=[]
with open(MATRIX,encoding="utf-8-sig",newline="") as f:
    for r in csv.DictReader(f):
        if is_good_row(r):
            rows.append(r)

ready=[]
needs=[]
processed=0
failed=0

for r in rows[:MAX_FILES]:
    path=r.get("path")
    key=sha(path+"|"+r.get("drive_id","")+"|"+r.get("size",""))

    text,err=rclone_cat(path)
    if err:
        rec={
            "mission":MISSION,
            "key":key,
            "path":path,
            "status":"READ_FAILED",
            "error":err,
            "processed_at":now(),
            "original_modified":False
        }
        append(RESULTS,rec)
        append(LEDGER,rec)
        failed+=1
        processed+=1
        continue

    a=analyze(text,path)
    rec={
        "mission":MISSION,
        "key":key,
        "path":path,
        "score":r.get("score"),
        "categories":r.get("categories"),
        "metadata_code_score":r.get("code_score"),
        "content_hash":sha(text),
        "bytes_read":len(text.encode("utf-8","ignore")),
        **a,
        "processed_at":now(),
        "original_modified":False,
        "reprocess_required":False
    }

    append(RESULTS,rec)
    append(LEDGER,rec)

    flat={k:rec.get(k) for k in ["path","score","categories","metadata_code_score","status","has_code","has_test","runtime_marker","incomplete","outdated","ideas","content_hash"]}

    if rec["status"] in ["READY_TO_TEST","RUNTIME_CANDIDATE_NEEDS_TEST"]:
        ready.append(flat)
    else:
        needs.append(flat)

    processed+=1

def write_csv(path,data):
    if not data:
        path.write_text("",encoding="utf-8")
        return
    with open(path,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)

write_csv(READY,ready)
write_csv(NEEDS,needs)

summary={
    "mission":MISSION,
    "timestamp":now(),
    "eligible":len(rows),
    "processed":processed,
    "read_failed":failed,
    "ready_to_test":len(ready),
    "needs_review":len(needs),
    "max_files":MAX_FILES,
    "zip_extraction":"SKIPPED",
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "ready_csv":str(READY),
    "needs_csv":str(NEEDS),
    "ledger":str(LEDGER),
    "certification":"SMART_CONTENT_BATCH_V2_CERTIFIED"
}
SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
print(json.dumps(summary,indent=2,ensure_ascii=True))
