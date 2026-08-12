import csv, json, re, hashlib
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91K3C_MATRIX_ID_AUDIT"
ROOT=Path(r"_evidence\P4.91K3C_MATRIX_ID_AUDIT_20260623_163953")
MATRIX=Path(r"_evidence\P4.91H_TO_O_PARALLEL_CAPABILITY_MATRIX_20260623_092058\reports\capability_matrix.csv")
PLAN=Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P4.91K2_FAST_READ_FAILED_METADATA_DIAGNOSTICS_20260623_134059\reports\recovery_plan.csv")

AUDIT=ROOT/"reports"/"matrix_id_audit.csv"
SAMPLE=ROOT/"reports"/"sample_100_targets.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91K3C_CERTIFICATION.txt"

ID_FIELDS=["drive_id","id","file_id","source_id","google_id","gdrive_id"]
PATH_FIELDS=["path","source_path","remote_path","original_path"]

def now():
    return datetime.now(timezone.utc).isoformat()

def looks_like_drive_id(x):
    if not x:
        return False
    x=str(x).strip()
    if len(x) < 20:
        return False
    if "/" in x or "\\" in x or " " in x:
        return False
    return bool(re.match(r"^[A-Za-z0-9_-]+$",x))

def load_matrix():
    rows={}
    headers=[]
    with open(MATRIX,encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        headers=reader.fieldnames or []
        for r in reader:
            p=r.get("path","")
            if p:
                rows[p]=r
    return headers,rows

def load_targets():
    out=[]
    with open(PLAN,encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            if r.get("reason")=="HIGH_VALUE_TIMEOUT" and r.get("priority")=="HIGH":
                out.append(r)
    return out

headers,matrix=load_matrix()
targets=load_targets()

audit_rows=[]
sample_rows=[]

counts={
    "targets":len(targets),
    "matched_matrix_path":0,
    "missing_matrix_path":0,
    "has_drive_id_field":0,
    "valid_drive_id_shape":0,
    "missing_id":0,
    "ingest_artifact":0,
    "control_artifact":0,
    "likely_real_drive_file":0,
    "invalid_id_shape":0
}

for i,t in enumerate(targets):
    p=t.get("path","")
    m=matrix.get(p)
    status=[]
    id_value=""
    id_field=""

    if not m:
        counts["missing_matrix_path"]+=1
        status.append("MISSING_MATRIX_ROW")
    else:
        counts["matched_matrix_path"]+=1

        for f in ID_FIELDS:
            if f in m and str(m.get(f,"")).strip():
                id_field=f
                id_value=str(m.get(f,"")).strip()
                break

        if id_value:
            counts["has_drive_id_field"]+=1
            if looks_like_drive_id(id_value):
                counts["valid_drive_id_shape"]+=1
                status.append("VALID_ID_SHAPE")
            else:
                counts["invalid_id_shape"]+=1
                status.append("INVALID_ID_SHAPE")
        else:
            counts["missing_id"]+=1
            status.append("MISSING_ID")

    low=p.lower()
    if "mind_v2_kb_zips_processed" in low or "/ingest/" in low:
        counts["ingest_artifact"]+=1
        status.append("INGEST_ARTIFACT")

    if low.startswith("_control/") or low.startswith("control/") or "evidence" in low or "report" in low or "ledger" in low:
        counts["control_artifact"]+=1
        status.append("CONTROL_OR_EVIDENCE_ARTIFACT")

    if id_value and looks_like_drive_id(id_value) and "INGEST_ARTIFACT" not in status:
        counts["likely_real_drive_file"]+=1
        status.append("LIKELY_REAL_DRIVE_FILE")

    rec={
        "path":p,
        "matrix_found":bool(m),
        "id_field":id_field,
        "id_value":id_value,
        "valid_id_shape":looks_like_drive_id(id_value),
        "classification":"|".join(status) if status else "UNCLASSIFIED",
        "reason":t.get("reason"),
        "priority":t.get("priority"),
        "recovery_action":t.get("recovery_action")
    }

    audit_rows.append(rec)

    if i < 100:
        sample_rows.append(rec)

def write_csv(path,data):
    if not data:
        path.write_text("",encoding="utf-8")
        return
    with open(path,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)

write_csv(AUDIT,audit_rows)
write_csv(SAMPLE,sample_rows)

summary={
    "mission":MISSION,
    "timestamp":now(),
    "matrix":str(MATRIX),
    "recovery_plan":str(PLAN),
    "matrix_headers":headers,
    "counts":counts,
    "audit_csv":str(AUDIT),
    "sample_csv":str(SAMPLE),
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "next":"P4.91K3D_RECOVERY_METHOD_FIX",
    "certification":"MATRIX_ID_AUDIT_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")

print(json.dumps(summary,indent=2,ensure_ascii=True))
