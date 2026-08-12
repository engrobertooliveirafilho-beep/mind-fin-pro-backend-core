import json, csv, hashlib, time, threading
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91K2_FAST_READ_FAILED_METADATA_DIAGNOSTICS"
ROOT=Path(r"_evidence\P4.91K2_FAST_READ_FAILED_METADATA_DIAGNOSTICS_20260623_134059")
RESULTS=Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P4.91K_SMART_CONTENT_EXTRACTOR_WITH_MONITOR_20260623_122120\exports\content_results.jsonl")

OUT=ROOT/"exports"/"read_failed_fast_diag.jsonl"
MATRIX=ROOT/"reports"/"read_failed_fast_matrix.csv"
RECOVERY=ROOT/"reports"/"recovery_plan.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91K2_FAST_CERTIFICATION.txt"

SKIP_PATTERNS=[
 "_evidence/","/evidence/","audit","auditoria","ledger","snapshot",
 "report","reports","final_truth","live_sequence","regression",
 "site-packages","__pycache__",".venv","venv/","node_modules",
 "coverage","dist-info","egg-info",".pytest_cache",".cache"
]

HIGH_VALUE_PATTERNS=[
 "runtime","engine","memory","retrieval","vector","agent","orchestrator",
 "workflow","whatsapp","twilio","supabase","pgvector","fastapi","router",
 "classifier","extractor","knowledge","context","semantic","graph",
 "eldora","mind","neura","schema","sql"
]

BINARY_EXT=[
 ".png",".jpg",".jpeg",".gif",".webp",".ico",".mp3",".mp4",".mov",
 ".pdf",".zip",".pyc"
]

state={
 "running":True,
 "started":time.time(),
 "total":0,
 "checked":0,
 "skipped_low_value":0,
 "timeout":0,
 "binary":0,
 "google_export":0,
 "retry":0,
 "unknown":0,
 "last_path":"",
 "last_reason":"",
 "last_action":""
}

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(x):
    return hashlib.sha256(str(x).encode("utf-8","ignore")).hexdigest()

def append(path,obj):
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj,ensure_ascii=True)+"\n")

def load_failed():
    out=[]
    seen=set()
    with open(RESULTS,encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                j=json.loads(line)
            except:
                continue
            if j.get("status")!="READ_FAILED":
                continue
            p=j.get("path","")
            if not p or p in seen:
                continue
            seen.add(p)
            out.append(j)
    return out

def classify(path, old_error):
    p=path.lower()
    ext=Path(p).suffix.lower()

    if any(x in p for x in SKIP_PATTERNS):
        return "LOW_VALUE_EVIDENCE_OR_DEPENDENCY", "SKIP_METADATA_ONLY", "LOW"

    if ext in BINARY_EXT:
        return "BINARY_FILE", "SKIP_BINARY_METADATA_ONLY", "LOW"

    if "google" in str(old_error).lower() or "export" in str(old_error).lower():
        return "GOOGLE_EXPORT_REQUIRED", "EXPORT_AS_TEXT_LATER", "HIGH"

    if any(x in p for x in HIGH_VALUE_PATTERNS):
        return "HIGH_VALUE_TIMEOUT", "RETRY_WITH_LONG_TIMEOUT_OR_COPY_LOCAL", "HIGH"

    if "timeout" in str(old_error).lower():
        return "TIMEOUT", "RETRY_ONCE_30S_THEN_SKIP", "MEDIUM"

    return "UNKNOWN", "REVIEW_LATER", "LOW"

def bump(reason):
    if reason=="LOW_VALUE_EVIDENCE_OR_DEPENDENCY":
        state["skipped_low_value"]+=1
    elif "TIMEOUT" in reason:
        state["timeout"]+=1
    elif reason=="BINARY_FILE":
        state["binary"]+=1
    elif reason=="GOOGLE_EXPORT_REQUIRED":
        state["google_export"]+=1
    elif reason=="HIGH_VALUE_TIMEOUT":
        state["retry"]+=1
    else:
        state["unknown"]+=1

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
        print("P4.91K2 FAST METADATA DIAGNOSTICS MONITOR")
        print("="*110)
        print(f"Elapsed............. {d} dias {h:02d}:{m:02d}:{sec:02d}")
        print(f"Total Failed........ {state['total']}")
        print(f"Checked............. {state['checked']}")
        print(f"Pending............. {max(state['total']-state['checked'],0)}")
        print("-"*110)
        print(f"Skip Low Value...... {state['skipped_low_value']}")
        print(f"Timeout............. {state['timeout']}")
        print(f"High Retry.......... {state['retry']}")
        print(f"Binary.............. {state['binary']}")
        print(f"Google Export....... {state['google_export']}")
        print(f"Unknown............. {state['unknown']}")
        print("-"*110)
        print(fit("Last Path........... "+state["last_path"]))
        print(fit("Last Reason......... "+state["last_reason"]))
        print(fit("Last Action......... "+state["last_action"]))
        print("="*110)
        time.sleep(5)

failed=load_failed()
state["total"]=len(failed)

mon=threading.Thread(target=monitor,daemon=True)
mon.start()

rows=[]
plans=[]
counts={}

for item in failed:
    path=item.get("path","")
    old_error=item.get("error","")
    reason,action,priority=classify(path,old_error)

    rec={
        "mission":MISSION,
        "diagnostic_key":sha(path),
        "path":path,
        "old_error":old_error,
        "reason":reason,
        "recovery_action":action,
        "priority":priority,
        "original_modified":False,
        "diagnosed_at":now()
    }

    rows.append(rec)
    plans.append({
        "path":path,
        "reason":reason,
        "recovery_action":action,
        "priority":priority
    })

    counts[reason]=counts.get(reason,0)+1
    append(OUT,rec)
    bump(reason)

    state["checked"]+=1
    state["last_path"]=path
    state["last_reason"]=reason
    state["last_action"]=action

def write_csv(path,data):
    if not data:
        path.write_text("",encoding="utf-8")
        return
    with open(path,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)

write_csv(MATRIX,rows)
write_csv(RECOVERY,plans)

summary={
    "mission":MISSION,
    "timestamp":now(),
    "source_results":str(RESULTS),
    "read_failed_total_unique":len(failed),
    "diagnosed_this_run":len(rows),
    "by_reason":counts,
    "matrix":str(MATRIX),
    "recovery_plan":str(RECOVERY),
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "next":"P4.91K3_TARGETED_RECOVERY_HIGH_PRIORITY_ONLY",
    "certification":"FAST_METADATA_DIAGNOSTICS_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")

state["running"]=False
time.sleep(1)

print("")
print("=== P4.91K2 FAST SUMMARY ===")
print(json.dumps(summary,indent=2,ensure_ascii=True))
