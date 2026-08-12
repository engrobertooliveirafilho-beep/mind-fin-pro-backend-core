import csv, json, subprocess, hashlib, time, threading, os
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91K_SMART_CONTENT_EXTRACTOR_WITH_MONITOR"
ROOT=Path(r"_evidence\P4.91K_SMART_CONTENT_EXTRACTOR_WITH_MONITOR_20260623_122120")
MATRIX=Path(r"_evidence\P4.91H_TO_O_PARALLEL_CAPABILITY_MATRIX_20260623_092058\reports\capability_matrix.csv")
ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

LEDGER=ROOT/"ledger"/"ledger.jsonl"
RESULTS=ROOT/"exports"/"content_results.jsonl"
READY=ROOT/"reports"/"ready_to_test.csv"
NEEDS=ROOT/"reports"/"needs_review.csv"
IDEAS=ROOT/"reports"/"ideas_real_content.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91K_CERTIFICATION.txt"

MAX_FILES=1000
MAX_BYTES=300000
TIMEOUT=8

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

state={
 "processed":0,
 "eligible":0,
 "ready":0,
 "needs":0,
 "failed":0,
 "last_path":"",
 "last_status":"",
 "last_ideas":"",
 "running":True,
 "started":time.time()
}

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

    if sc < 4: return False
    if r.get("kind") == "ZIP": return False
    if ext not in GOOD_EXT: return False
    if any(b in path for b in BAD): return False
    if not any(c in cats for c in GOOD_CATS): return False
    return True

def rclone_cat(path):
    cmd=["rclone","cat","gdrive:"+path,"--drive-root-folder-id",ROOT_ID]
    try:
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None,"TIMEOUT_8S"
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

def fit(s,w=110):
    s=str(s or "")
    if len(s)>w:
        s=s[:w-3]+"..."
    return s.ljust(w)

def monitor():
    while state["running"]:
        elapsed=int(time.time()-state["started"])
        d=elapsed//86400
        h=(elapsed%86400)//3600
        m=(elapsed%3600)//60
        sec=elapsed%60

        print("")
        print("="*110)
        print("P4.91K SMART CONTENT EXTRACTOR WITH MONITOR")
        print("="*110)
        print(f"Elapsed............. {d} dias {h:02d}:{m:02d}:{sec:02d}")
        print(f"Eligible............ {state['eligible']}")
        print(f"Processed........... {state['processed']}")
        print(f"Ready To Test....... {state['ready']}")
        print(f"Needs Review........ {state['needs']}")
        print(f"Read Failed......... {state['failed']}")
        print("-"*110)
        print("ULTIMO ITEM")
        print(fit('Path................. '+state['last_path']))
        print(fit('Status............... '+state['last_status']))
        print(fit('Ideas................ '+state['last_ideas']))
        print("="*110)
        time.sleep(10)

rows=[]
with open(MATRIX,encoding="utf-8-sig",newline="") as f:
    for r in csv.DictReader(f):
        if is_good_row(r):
            rows.append(r)

state["eligible"]=len(rows)

mon=threading.Thread(target=monitor,daemon=True)
mon.start()

ready=[]
needs=[]
idea_rows=[]
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
        state["failed"]=failed
        state["processed"]=processed
        state["last_path"]=path
        state["last_status"]="READ_FAILED"
        state["last_ideas"]=""
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
        state["ready"]=len(ready)
    else:
        needs.append(flat)
        state["needs"]=len(needs)

    for idea in (rec.get("ideas") or "").split("|"):
        if idea:
            idea_rows.append({
                "idea":idea,
                "source_path":path,
                "score":r.get("score"),
                "categories":r.get("categories"),
                "status":rec["status"],
                "has_code":rec["has_code"],
                "runtime_marker":rec["runtime_marker"]
            })

    processed+=1
    state["processed"]=processed
    state["last_path"]=path
    state["last_status"]=rec["status"]
    state["last_ideas"]=rec.get("ideas","")

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
write_csv(IDEAS,idea_rows)

summary={
    "mission":MISSION,
    "timestamp":now(),
    "eligible":len(rows),
    "processed":processed,
    "read_failed":failed,
    "ready_to_test":len(ready),
    "needs_review":len(needs),
    "ideas_real_content":len(idea_rows),
    "max_files":MAX_FILES,
    "zip_extraction":"SKIPPED",
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "ready_csv":str(READY),
    "needs_csv":str(NEEDS),
    "ideas_csv":str(IDEAS),
    "ledger":str(LEDGER),
    "certification":"SMART_CONTENT_EXTRACTOR_WITH_MONITOR_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")

state["running"]=False
time.sleep(1)

print("")
print("=== CERTIFICATION ===")
print(CERT.read_text(encoding="utf-8"))
print("")
print("=== SUMMARY ===")
print(json.dumps(summary,indent=2,ensure_ascii=True))
