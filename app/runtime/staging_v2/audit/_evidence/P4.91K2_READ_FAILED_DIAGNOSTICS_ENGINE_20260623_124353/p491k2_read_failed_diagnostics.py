import json, csv, subprocess, hashlib, time
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91K2_READ_FAILED_DIAGNOSTICS_ENGINE"
ROOT=Path(r"_evidence\P4.91K2_READ_FAILED_DIAGNOSTICS_ENGINE_20260623_124353")
RESULTS=Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P4.91K_SMART_CONTENT_EXTRACTOR_WITH_MONITOR_20260623_122120\exports\content_results.jsonl")
ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

OUT=ROOT/"exports"/"read_failed_diagnostics.jsonl"
MATRIX=ROOT/"reports"/"read_failed_matrix.csv"
RECOVERY=ROOT/"reports"/"recovery_plan.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91K2_CERTIFICATION.txt"

MAX_CHECK=1000

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
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=20)
    except subprocess.TimeoutExpired:
        return None,"TIMEOUT_LSJSON_20S"
    except Exception as e:
        return None,"LSJSON_EXCEPTION:"+str(e)

    if p.returncode != 0:
        return None,(p.stderr or b"").decode("utf-8","replace")[-2000:]
    try:
        raw=(p.stdout or b"[]").decode("utf-8","replace")
        return json.loads(raw or "[]"),None
    except Exception as e:
        return None,"JSON_PARSE_ERROR:"+str(e)

def rclone_cat_probe(path,timeout=20):
    cmd=["rclone","cat","gdrive:"+path,"--drive-root-folder-id",ROOT_ID]
    try:
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=timeout)
    except subprocess.TimeoutExpired:
        return None,"TIMEOUT_CAT_"+str(timeout)+"S"
    except Exception as e:
        return None,"CAT_EXCEPTION:"+str(e)

    if p.returncode != 0:
        return None,(p.stderr or b"").decode("utf-8","replace")[-2000:]

    data=p.stdout or b""
    return len(data),None

def classify_error(path, old_error, ls_err, cat_err, meta):
    p=path.lower()
    combined=" ".join([str(old_error),str(ls_err),str(cat_err)]).lower()

    if "timeout" in combined:
        reason="TIMEOUT"
    elif "permission" in combined or "access denied" in combined or "403" in combined:
        reason="PERMISSION_DENIED"
    elif "not found" in combined or "404" in combined or "directory not found" in combined:
        reason="PATH_ERROR"
    elif any(x in p for x in [".png",".jpg",".jpeg",".gif",".webp",".ico",".mp3",".mp4",".mov",".pdf"]):
        reason="BINARY_FILE"
    elif "google document" in combined or "docs.google" in combined:
        reason="GOOGLE_DOC"
    elif "google spreadsheet" in combined:
        reason="GOOGLE_SHEET"
    elif "google presentation" in combined:
        reason="GOOGLE_SLIDE"
    elif "can't download" in combined or "export" in combined:
        reason="GOOGLE_EXPORT_REQUIRED"
    elif meta and isinstance(meta,list) and len(meta)>0:
        size=meta[0].get("Size")
        if isinstance(size,int) and size > 5000000:
            reason="TOO_LARGE"
        else:
            reason="RCLONE_CAT_FAILED"
    else:
        reason="UNKNOWN"

    return reason

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

failed=load_failed()
rows=[]
plans=[]
counts={}
checked=0

for item in failed[:MAX_CHECK]:
    path=item.get("path","")
    old_error=item.get("error","")

    meta,ls_err=rclone_lsf(path)
    probe,cat_err=rclone_cat_probe(path,timeout=20)

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
    append(OUT,rec)
    checked+=1

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
    "certification":"READ_FAILED_DIAGNOSTICS_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")

print(json.dumps(summary,indent=2,ensure_ascii=True))
