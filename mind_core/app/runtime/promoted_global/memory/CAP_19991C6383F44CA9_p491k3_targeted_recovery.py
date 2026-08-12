import csv, json, subprocess, hashlib, time, threading, re
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91K3_TARGETED_RECOVERY_HIGH_PRIORITY_ONLY"
ROOT=Path(r"_evidence\P4.91K3_TARGETED_RECOVERY_HIGH_PRIORITY_ONLY_20260623_144202")
PLAN=Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P4.91K2_FAST_READ_FAILED_METADATA_DIAGNOSTICS_20260623_134059\reports\recovery_plan.csv")
ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

STAGING=ROOT/"staging"
LEDGER=ROOT/"ledger"/"recovery_ledger.jsonl"
RESULTS=ROOT/"exports"/"recovery_results.jsonl"
READY=ROOT/"reports"/"recovered_ready_to_test.csv"
NEEDS=ROOT/"reports"/"recovered_needs_review.csv"
IDEAS=ROOT/"reports"/"recovered_ideas.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91K3_CERTIFICATION.txt"

MAX_RECOVER=427
COPY_TIMEOUT=60
MAX_BYTES=500000

state={
 "running":True,
 "started":time.time(),
 "eligible":0,
 "processed":0,
 "recovered":0,
 "failed":0,
 "ready":0,
 "needs":0,
 "last_path":"",
 "last_status":"",
 "last_error":""
}

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(x):
    return hashlib.sha256(str(x).encode("utf-8","ignore")).hexdigest()

def safe_name(s):
    s=re.sub(r"[^A-Za-z0-9_.-]+","_",s)
    return s[-180:]

def append(path,obj):
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj,ensure_ascii=True)+"\n")

def load_targets():
    rows=[]
    with open(PLAN,encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            if r.get("reason")=="HIGH_VALUE_TIMEOUT" and r.get("priority")=="HIGH":
                rows.append(r)
    return rows

def copy_local(remote_path):
    local=STAGING/(sha(remote_path)+"_"+safe_name(Path(remote_path).name))
    cmd=[
        "rclone","copyto",
        "gdrive:"+remote_path,
        str(local),
        "--drive-root-folder-id",ROOT_ID,
        "--retries","1",
        "--low-level-retries","1",
        "--transfers","1",
        "--checkers","1"
    ]
    try:
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=COPY_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None,"COPY_TIMEOUT_60S"
    except Exception as e:
        return None,("COPY_EXCEPTION:"+str(e))[:1000]

    if p.returncode != 0:
        return None,(p.stderr or b"").decode("utf-8","replace")[-1500:]

    if not local.exists():
        return None,"LOCAL_FILE_NOT_CREATED"

    return local,None

def read_local(local):
    try:
        data=local.read_bytes()
        if len(data)>MAX_BYTES:
            data=data[:MAX_BYTES]
        return data.decode("utf-8","replace"),None
    except Exception as e:
        return None,("LOCAL_READ_EXCEPTION:"+str(e))[:1000]

def analyze(text,path):
    low=(text or "").lower()
    p=path.lower()

    has_code=any(x in low for x in [
        "def ","class ","import ","from ","function ","const ","let ","async ","await ",
        "fastapi","router","select ","create table","oninit","input "
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
    for k in ["memory","retrieval","rag","vector","embedding","agent","runtime","orchestrator","workflow","whatsapp","twilio","supabase","fastapi","ledger","classifier","extractor","knowledge","context","semantic","graph","eldora","mind","schema","sql"]:
        if k in low or k in p:
            ideas.append(k.upper())

    return {
        "status":status,
        "has_code":has_code,
        "has_test":has_test,
        "runtime_marker":runtime,
        "incomplete":incomplete,
        "outdated":outdated,
        "ideas":"|".join(sorted(set(ideas))[:30])
    }

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
        print("P4.91K3 TARGETED HIGH PRIORITY RECOVERY MONITOR")
        print("="*110)
        print(f"Elapsed............. {d} dias {h:02d}:{m:02d}:{sec:02d}")
        print(f"Eligible............ {state['eligible']}")
        print(f"Processed........... {state['processed']}")
        print(f"Recovered........... {state['recovered']}")
        print(f"Failed.............. {state['failed']}")
        print(f"Ready To Test....... {state['ready']}")
        print(f"Needs Review........ {state['needs']}")
        print("-"*110)
        print(fit("Last Path........... "+state["last_path"]))
        print(fit("Last Status......... "+state["last_status"]))
        print(fit("Last Error.......... "+state["last_error"]))
        print("="*110)
        time.sleep(10)

targets=load_targets()
state["eligible"]=len(targets)

mon=threading.Thread(target=monitor,daemon=True)
mon.start()

ready=[]
needs=[]
idea_rows=[]

for r in targets[:MAX_RECOVER]:
    path=r.get("path","")
    key=sha(path)

    local,err=copy_local(path)

    if err:
        rec={
            "mission":MISSION,
            "key":key,
            "path":path,
            "status":"RECOVERY_FAILED",
            "error":err,
            "original_modified":False,
            "processed_at":now()
        }
        append(RESULTS,rec)
        append(LEDGER,rec)

        state["processed"]+=1
        state["failed"]+=1
        state["last_path"]=path
        state["last_status"]="RECOVERY_FAILED"
        state["last_error"]=err
        continue

    text,err=read_local(local)

    if err:
        rec={
            "mission":MISSION,
            "key":key,
            "path":path,
            "local_path":str(local),
            "status":"LOCAL_READ_FAILED",
            "error":err,
            "original_modified":False,
            "processed_at":now()
        }
        append(RESULTS,rec)
        append(LEDGER,rec)

        state["processed"]+=1
        state["failed"]+=1
        state["last_path"]=path
        state["last_status"]="LOCAL_READ_FAILED"
        state["last_error"]=err
        continue

    a=analyze(text,path)

    rec={
        "mission":MISSION,
        "key":key,
        "path":path,
        "local_staging":str(local),
        "content_hash":sha(text),
        "bytes_read":len(text.encode("utf-8","ignore")),
        **a,
        "status_after_recovery":a["status"],
        "original_modified":False,
        "processed_at":now()
    }

    append(RESULTS,rec)
    append(LEDGER,rec)

    flat={
        "path":path,
        "local_staging":str(local),
        "status":a["status"],
        "has_code":a["has_code"],
        "has_test":a["has_test"],
        "runtime_marker":a["runtime_marker"],
        "incomplete":a["incomplete"],
        "outdated":a["outdated"],
        "ideas":a["ideas"],
        "content_hash":rec["content_hash"]
    }

    if a["status"] in ["READY_TO_TEST","RUNTIME_CANDIDATE_NEEDS_TEST"]:
        ready.append(flat)
        state["ready"]=len(ready)
    else:
        needs.append(flat)
        state["needs"]=len(needs)

    for idea in (a["ideas"] or "").split("|"):
        if idea:
            idea_rows.append({
                "idea":idea,
                "source_path":path,
                "status":a["status"],
                "has_code":a["has_code"],
                "runtime_marker":a["runtime_marker"]
            })

    state["processed"]+=1
    state["recovered"]+=1
    state["last_path"]=path
    state["last_status"]=a["status"]
    state["last_error"]=""

write_csv(READY,ready)
write_csv(NEEDS,needs)
write_csv(IDEAS,idea_rows)

summary={
    "mission":MISSION,
    "timestamp":now(),
    "source_recovery_plan":str(PLAN),
    "eligible_high_value_timeout":len(targets),
    "processed":state["processed"],
    "recovered":state["recovered"],
    "failed":state["failed"],
    "ready_to_test":len(ready),
    "needs_review":len(needs),
    "ideas":len(idea_rows),
    "staging":str(STAGING),
    "ready_csv":str(READY),
    "needs_csv":str(NEEDS),
    "ideas_csv":str(IDEAS),
    "ledger":str(LEDGER),
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "certification":"TARGETED_HIGH_PRIORITY_RECOVERY_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")

state["running"]=False
time.sleep(1)

print("")
print("=== P4.91K3 SUMMARY ===")
print(json.dumps(summary,indent=2,ensure_ascii=True))
