import csv, json, subprocess, hashlib, time, threading, re, ast
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91L2_STAGING_COPY_AND_TEST"
ROOT=Path(r"_evidence\P4.91L2_STAGING_COPY_AND_TEST_20260623_170841")
READY=Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P4.91L_CODE_RECOVERY_ENGINE_20260623_170102\reports\runtime_test_candidates.csv")
ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

STAGING=ROOT/"staging"
RESULTS=ROOT/"exports"/"staging_test_results.jsonl"
LEDGER=ROOT/"ledger"/"staging_test_ledger.jsonl"
MATRIX=ROOT/"reports"/"integration_matrix.csv"
READY_OUT=ROOT/"reports"/"integration_ready.csv"
NEEDS_OUT=ROOT/"reports"/"integration_needs_fix.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91L2_CERTIFICATION.txt"

MAX_FILES=200
COPY_TIMEOUT=60
MAX_BYTES=800000

state={"running":True,"started":time.time(),"eligible":0,"processed":0,"copied":0,"copy_failed":0,"syntax_ok":0,"syntax_fail":0,"integration_ready":0,"needs_fix":0,"last_path":"","last_status":"","last_error":""}

def now(): return datetime.now(timezone.utc).isoformat()
def sha(x): return hashlib.sha256(str(x).encode("utf-8","ignore")).hexdigest()
def safe(s): return re.sub(r"[^A-Za-z0-9_.-]+","_",s)[-150:]

def append(p,o):
    with open(p,"a",encoding="utf-8") as f:
        f.write(json.dumps(o,ensure_ascii=True)+"\n")

def load_targets():
    rows=[]
    with open(READY,encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            if r.get("tier")=="TIER_1_RUNTIME_TEST":
                rows.append(r)
    return rows

def copy_file(path):
    local=STAGING/(sha(path)+"_"+safe(Path(path).name))
    cmd=[
        "rclone","copyto",
        "gdrive:"+path,
        str(local),
        "--drive-root-folder-id",ROOT_ID,
        "--retries","1",
        "--low-level-retries","1",
        "--transfers","1",
        "--checkers","1",
        "--tpslimit","1",
        "--tpslimit-burst","1"
    ]
    try:
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=COPY_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None,"COPY_TIMEOUT_60S"
    except Exception as e:
        return None,("COPY_EXCEPTION:"+str(e))[:1000]
    if p.returncode!=0:
        return None,(p.stderr or b"").decode("utf-8","replace")[-1500:]
    if not local.exists():
        return None,"LOCAL_FILE_NOT_CREATED"
    return local,None

def read_text(local):
    try:
        data=local.read_bytes()
        if len(data)>MAX_BYTES:
            data=data[:MAX_BYTES]
        return data.decode("utf-8","replace"),None
    except Exception as e:
        return "",("READ_EXCEPTION:"+str(e))[:1000]

def syntax_check(local,text):
    ext=local.suffix.lower()
    if ext==".py":
        try:
            ast.parse(text)
            return "SYNTAX_OK",""
        except Exception as e:
            return "SYNTAX_FAIL",str(e)[:1000]
    if ext==".json":
        try:
            json.loads(text)
            return "SYNTAX_OK",""
        except Exception as e:
            return "SYNTAX_FAIL",str(e)[:1000]
    return "SYNTAX_NOT_APPLICABLE",""

def deps(text):
    found=set()
    low=text.lower()
    for k in ["fastapi","uvicorn","pydantic","requests","httpx","supabase","psycopg","pgvector","openai","twilio","pandas","numpy","sqlalchemy","pytest","redis","celery"]:
        if k in low:
            found.add(k)
    return "|".join(sorted(found))

def integration_status(path,text,syntax_status):
    low=text.lower()
    p=path.lower()
    runtime=any(x in low or x in p for x in ["fastapi","router","webhook","runtime","worker","twilio","supabase","pgvector"])
    tests=any(x in low for x in ["pytest","unittest","assert ","test_"])
    incomplete=any(x in low or x in p for x in ["todo","fixme","not implemented","placeholder","pending","incomplete","failed","abort"])
    dangerous=any(x in low for x in ["delete(","shutil.rmtree","drop table","remove-item","rm -rf"])
    if syntax_status=="SYNTAX_FAIL":
        return "NEEDS_FIX_SYNTAX"
    if dangerous:
        return "NEEDS_SECURITY_REVIEW"
    if incomplete:
        return "NEEDS_COMPLETION"
    if runtime and tests:
        return "INTEGRATION_READY_WITH_TESTS"
    if runtime:
        return "INTEGRATION_READY_NEEDS_TESTS"
    return "CODE_REVIEW_ONLY"

def write_csv(path,data):
    if not data:
        path.write_text("",encoding="utf-8")
        return
    with open(path,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)

def fit(s,w=110):
    s=str(s or "")
    return (s[:w-3]+"..." if len(s)>w else s).ljust(w)

def monitor():
    while state["running"]:
        e=int(time.time()-state["started"])
        print("")
        print("="*110)
        print("P4.91L2 STAGING COPY AND TEST MONITOR")
        print("="*110)
        print(f"Elapsed............. {e//86400} dias {(e%86400)//3600:02d}:{(e%3600)//60:02d}:{e%60:02d}")
        print(f"Eligible............ {state['eligible']}")
        print(f"Processed........... {state['processed']}")
        print(f"Copied.............. {state['copied']}")
        print(f"Copy Failed......... {state['copy_failed']}")
        print(f"Syntax OK........... {state['syntax_ok']}")
        print(f"Syntax Fail......... {state['syntax_fail']}")
        print(f"Integration Ready... {state['integration_ready']}")
        print(f"Needs Fix........... {state['needs_fix']}")
        print("-"*110)
        print(fit("Last Path........... "+state["last_path"]))
        print(fit("Last Status......... "+state["last_status"]))
        print(fit("Last Error.......... "+state["last_error"]))
        print("="*110)
        time.sleep(10)

targets=load_targets()
state["eligible"]=len(targets)
threading.Thread(target=monitor,daemon=True).start()

all_rows=[]
ready_rows=[]
needs_rows=[]

for r in targets[:MAX_FILES]:
    path=r.get("path","")
    local,err=copy_file(path)

    if err:
        rec={"mission":MISSION,"path":path,"status":"COPY_FAILED","error":err,"original_modified":False,"processed_at":now()}
        append(RESULTS,rec); append(LEDGER,rec)
        state["processed"]+=1; state["copy_failed"]+=1; state["last_path"]=path; state["last_status"]="COPY_FAILED"; state["last_error"]=err
        needs_rows.append(rec)
        continue

    text,err=read_text(local)
    syntax_status,syntax_error=syntax_check(local,text)
    istatus=integration_status(path,text,syntax_status)
    dep=deps(text)

    rec={
        "mission":MISSION,
        "path":path,
        "local_staging":str(local),
        "tier":r.get("tier"),
        "score":r.get("score"),
        "code_score":r.get("code_score"),
        "categories":r.get("categories"),
        "syntax_status":syntax_status,
        "syntax_error":syntax_error,
        "dependencies":dep,
        "integration_status":istatus,
        "bytes_read":len(text.encode("utf-8","ignore")),
        "content_hash":sha(text),
        "original_modified":False,
        "processed_at":now()
    }

    append(RESULTS,rec); append(LEDGER,rec)
    all_rows.append(rec)

    state["processed"]+=1
    state["copied"]+=1
    if syntax_status=="SYNTAX_OK": state["syntax_ok"]+=1
    if syntax_status=="SYNTAX_FAIL": state["syntax_fail"]+=1

    if istatus in ["INTEGRATION_READY_WITH_TESTS","INTEGRATION_READY_NEEDS_TESTS"]:
        ready_rows.append(rec); state["integration_ready"]=len(ready_rows)
    else:
        needs_rows.append(rec); state["needs_fix"]=len(needs_rows)

    state["last_path"]=path
    state["last_status"]=istatus
    state["last_error"]=syntax_error

write_csv(MATRIX,all_rows)
write_csv(READY_OUT,ready_rows)
write_csv(NEEDS_OUT,needs_rows)

summary={
    "mission":MISSION,
    "timestamp":now(),
    "source_ready":str(READY),
    "eligible_tier_1_runtime":len(targets),
    "max_files_this_run":MAX_FILES,
    "processed":state["processed"],
    "copied":state["copied"],
    "copy_failed":state["copy_failed"],
    "syntax_ok":state["syntax_ok"],
    "syntax_fail":state["syntax_fail"],
    "integration_ready":len(ready_rows),
    "needs_fix_or_review":len(needs_rows),
    "matrix":str(MATRIX),
    "integration_ready_csv":str(READY_OUT),
    "needs_fix_csv":str(NEEDS_OUT),
    "ledger":str(LEDGER),
    "staging":str(STAGING),
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "next":"P4.91M_MIND_CAPABILITY_RECOVERY",
    "certification":"STAGING_COPY_AND_TEST_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")

state["running"]=False
time.sleep(1)
print("")
print("=== P4.91L2 SUMMARY ===")
print(json.dumps(summary,indent=2,ensure_ascii=True))
