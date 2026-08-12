import json, csv, subprocess, hashlib, time, threading
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91K2_READ_FAILED_DIAGNOSTICS_WITH_MONITOR"
ROOT=Path(r"_evidence\P4.91K2_READ_FAILED_DIAGNOSTICS_WITH_MONITOR_20260623_125318")
RESULTS=Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P4.91K_SMART_CONTENT_EXTRACTOR_WITH_MONITOR_20260623_122120\exports\content_results.jsonl")
ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

OUT=ROOT/"exports"/"read_failed_diagnostics.jsonl"
MATRIX=ROOT/"reports"/"read_failed_matrix.csv"
RECOVERY=ROOT/"reports"/"recovery_plan.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91K2_CERTIFICATION.txt"

MAX_CHECK=1000
LS_TIMEOUT=8
CAT_TIMEOUT=8

state={
 "running":True,
 "started":time.time(),
 "total":0,
 "checked":0,
 "timeout":0,
 "permission":0,
 "path_error":0,
 "binary":0,
 "export_required":0,
 "too_large":0,
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
            path=j.get("path","")
            if not path or path in seen:
                continue
            seen.add(path)
            out.append(j)
    return out

def rclone_lsf(path):
    cmd=["rclone","lsjson","gdrive:"+path,"--drive-root-folder-id",ROOT_ID,"--no-mimetype"]
    try:
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=LS_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None,"TIMEOUT_LSJSON"
    except Exception as e:
        return None,"LSJSON_EXCEPTION:"+str(e)

    if p.returncode != 0:
        return None,(p.stderr or b"").decode("utf-8","replace")[-1500:]

    try:
        raw=(p.stdout or b"[]").decode("utf-8","replace")
        return json.loads(raw or "[]"),None
    except Exception as e:
        return None,"JSON_PARSE_ERROR:"+str(e)

def rclone_cat_probe(path):
    cmd=["rclone","cat","gdrive:"+path,"--drive-root-folder-id",ROOT_ID]
    try:
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=CAT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None,"TIMEOUT_CAT"
    except Exception as e:
        return None,"CAT_EXCEPTION:"+str(e)

    if p.returncode != 0:
        return None,(p.stderr or b"").decode("utf-8","replace")[-1500:]

    data=p.stdout or b""
    return len(data),None

def classify_error(path, old_error, ls_err, cat_err, meta):
    p=path.lower()
    combined=" ".join([str(old_error),str(ls_err),str(cat_err)]).lower()

    if "timeout" in combined:
        return "TIMEOUT"
    if "permission" in combined or "access denied" in combined or "403" in combined:
        return "PERMISSION_DENIED"
    if "not found" in combined or "404" in combined or "directory not found" in combined:
        return "PATH_ERROR"
    if any(x in p for x in [".png",".jpg",".jpeg",".gif",".webp",".ico",".mp3",".mp4",".mov",".pdf"]):
        return "BINARY_FILE"
    if "google document" in combined or "docs.google" in combined:
        return "GOOGLE_DOC"
    if "google spreadsheet" in combined:
        return "GOOGLE_SHEET"
    if "google presentation" in combined:
        return "GOOGLE_SLIDE"
    if "can't download" in combined or "export" in combined:
        return "GOOGLE_EXPORT_REQUIRED"

    if meta and isinstance(meta,list) and len(meta)>0:
        size=meta[0].get("Size")
        if isinstance(size,int) and size > 5000000:
            return "TOO_LARGE"
        return "RCLONE_CAT_FAILED"

    return "UNKNOWN"

def recovery_action(reason,path):
    p=path.lower()

    if reason=="TIMEOUT":
        return "RETRY_WITH_30S_THEN_SKIP"
    if reason in ["GOOGLE_DOC","GOOGLE_EXPORT_REQUIRED"]:
        return "EXPORT_AS_TXT_OR_MD"
    if reason=="GOOGLE_SHEET":
        return "EXPORT_AS_CSV"
    if reason=="GOOGLE_SLIDE":
        return "EXPORT_AS_TXT"
    if reason=="TOO_LARGE":
        return "PARTIAL_READ_OR_METADATA_ONLY"
    if reason=="BINARY_FILE":
        return "SKIP_BINARY_METADATA_ONLY"
    if reason=="PERMISSION_DENIED":
        return "MARK_PERMISSION_BLOCKED"
    if reason=="PATH_ERROR":
        return "MARK_PATH_INVALID_OR_MOVED"
    if "site-packages" in p or "__pycache__" in p or "node_modules" in p:
        return "SKIP_DEPENDENCY_NO_RUNTIME_VALUE"
    return "RETRY_ONCE_THEN_REVIEW"

def bump(reason):
    if reason=="TIMEOUT":
        state["timeout"]+=1
    elif reason=="PERMISSION_DENIED":
        state["permission"]+=1
    elif reason=="PATH_ERROR":
        state["path_error"]+=1
    elif reason=="BINARY_FILE":
        state["binary"]+=1
    elif reason in ["GOOGLE_DOC","GOOGLE_SHEET","GOOGLE_SLIDE","GOOGLE_EXPORT_REQUIRED"]:
        state["export_required"]+=1
    elif reason=="TOO_LARGE":
        state["too_large"]+=1
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
        print("P4.91K2 READ_FAILED DIAGNOSTICS MONITOR")
        print("="*110)
        print(f"Elapsed............. {d} dias {h:02d}:{m:02d}:{sec:02d}")
        print(f"Total Failed........ {state['total']}")
        print(f"Checked............. {state['checked']}")
        print(f"Pending............. {max(state['total']-state['checked'],0)}")
        print("-"*110)
        print(f"TIMEOUT............. {state['timeout']}")
        print(f"PERMISSION.......... {state['permission']}")
        print(f"PATH_ERROR.......... {state['path_error']}")
        print(f"BINARY.............. {state['binary']}")
        print(f"EXPORT_REQUIRED..... {state['export_required']}")
        print(f"TOO_LARGE........... {state['too_large']}")
        print(f"UNKNOWN............. {state['unknown']}")
        print("-"*110)
        print(fit("Last Path........... "+state["last_path"]))
        print(fit("Last Reason......... "+state["last_reason"]))
        print(fit("Last Action......... "+state["last_action"]))
        print("="*110)
        time.sleep(10)

failed=load_failed()
state["total"]=len(failed)

mon=threading.Thread(target=monitor,daemon=True)
mon.start()

rows=[]
plans=[]
counts={}
checked=0

for item in failed[:MAX_CHECK]:
    path=item.get("path","")
    old_error=item.get("error","")

    meta,ls_err=rclone_lsf(path)
    probe,cat_err=rclone_cat_probe(path)

    reason=classify_error(path,old_error,ls_err,cat_err,meta)
    action=recovery_action(reason,path)

    rec={
        "mission":MISSION,
        "diagnostic_key":sha(path),
        "path":path,
        "old_error":old_error,
        "lsjson_error":ls_err,
        "cat_probe_error":cat_err,
        "cat_probe_bytes":probe,
        "reason":reason,
        "recovery_action":action,
        "priority":"HIGH" if action in ["EXPORT_AS_TXT_OR_MD","RETRY_WITH_30S_THEN_SKIP","EXPORT_AS_CSV"] else "LOW",
        "original_modified":False,
        "diagnosed_at":now()
    }

    rows.append(rec)
    plans.append({
        "path":path,
        "reason":reason,
        "recovery_action":action,
        "priority":rec["priority"]
    })

    counts[reason]=counts.get(reason,0)+1
    bump(reason)
    append(OUT,rec)

    checked+=1
    state["checked"]=checked
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
    "diagnosed_this_run":checked,
    "by_reason":counts,
    "matrix":str(MATRIX),
    "recovery_plan":str(RECOVERY),
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "next":"P4.91K3_READ_RECOVERY_ENGINE",
    "certification":"READ_FAILED_DIAGNOSTICS_WITH_MONITOR_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")

state["running"]=False
time.sleep(1)

print("")
print("=== P4.91K2 SUMMARY ===")
print(json.dumps(summary,indent=2,ensure_ascii=True))
