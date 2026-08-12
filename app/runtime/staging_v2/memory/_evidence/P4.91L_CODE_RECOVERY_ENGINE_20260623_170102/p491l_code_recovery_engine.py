import csv, json, hashlib, time
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91L_CODE_RECOVERY_ENGINE"
ROOT=Path(r"_evidence\P4.91L_CODE_RECOVERY_ENGINE_20260623_170102")
MATRIX=Path(r"_evidence\P4.91H_TO_O_PARALLEL_CAPABILITY_MATRIX_20260623_092058\reports\capability_matrix.csv")

CODE_MATRIX=ROOT/"reports"/"code_recovery_matrix.csv"
READY=ROOT/"reports"/"runtime_test_candidates.csv"
NEEDS=ROOT/"reports"/"code_needs_review.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91L_CERTIFICATION.txt"
LEDGER=ROOT/"ledger"/"code_recovery_ledger.jsonl"

BAD=[
 "mind_v2_kb_zips_processed","/ingest/","_control/","control/",
 "mind_evidence","_evidence","evidence","audit","auditoria",
 "report","reports","ledger","snapshot","final_truth",
 "node_modules","site-packages","__pycache__",".venv","venv/",
 ".pytest_cache",".cache","dist-info","egg-info","coverage",
 "license","licenses"
]

GOOD_EXT=[".py",".ps1",".js",".ts",".tsx",".jsx",".sql",".mq5",".mq4",".yaml",".yml",".json"]

RUNTIME_WORDS=[
 "runtime","engine","router","fastapi","worker","webhook","whatsapp",
 "twilio","supabase","pgvector","retrieval","memory","agent",
 "orchestrator","workflow","semantic","vector","classifier","extractor",
 "context","knowledge","eldora","mind","neura"
]

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(x):
    return hashlib.sha256(str(x).encode("utf-8","ignore")).hexdigest()

def tier(path,cats,score,code_score):
    p=path.lower()
    s=int(score or 0)
    cs=int(code_score or 0)

    if any(x in p for x in ["fastapi","runtime","router","webhook","worker","supabase","pgvector"]):
        return "TIER_1_RUNTIME_TEST"
    if any(x in p for x in ["memory","retrieval","vector","semantic","agent","orchestrator","workflow"]):
        return "TIER_2_CAPABILITY_TEST"
    if cs >= 5 and s >= 4:
        return "TIER_3_CODE_REVIEW"
    return "TIER_4_LOW_PRIORITY"

def status(path,t):
    p=path.lower()
    if any(x in p for x in ["todo","fix","failed","partial","pending","incomplete","abort"]):
        return "NEEDS_FIX"
    if any(x in p for x in ["old","legacy","legado","deprecated","obsolete","quarentena"]):
        return "OUTDATED_OR_QUARANTINE"
    if t in ["TIER_1_RUNTIME_TEST","TIER_2_CAPABILITY_TEST"]:
        return "READY_FOR_STAGING_TEST"
    return "CODE_REVIEW_ONLY"

rows=[]
ready=[]
needs=[]

with open(MATRIX,encoding="utf-8-sig",newline="") as f:
    for r in csv.DictReader(f):
        path=r.get("path","")
        p=path.lower()
        ext=Path(p).suffix.lower()

        if ext not in GOOD_EXT:
            continue
        if any(b in p for b in BAD):
            continue

        try:
            score=int(r.get("score") or 0)
            code_score=int(r.get("code_score") or 0)
        except:
            continue

        if code_score < 3:
            continue

        cats=r.get("categories","")
        t=tier(path,cats,score,code_score)
        st=status(path,t)

        rec={
            "key":sha(path+"|"+r.get("drive_id","")),
            "path":path,
            "drive_id":r.get("drive_id"),
            "name":r.get("name"),
            "kind":r.get("kind"),
            "size":r.get("size"),
            "mod_time":r.get("mod_time"),
            "categories":cats,
            "score":score,
            "code_score":code_score,
            "tier":t,
            "status":st,
            "ideas":r.get("ideas"),
            "original_modified":False,
            "certified_at":now()
        }

        rows.append(rec)
        if st=="READY_FOR_STAGING_TEST":
            ready.append(rec)
        else:
            needs.append(rec)

        with open(LEDGER,"a",encoding="utf-8") as lf:
            lf.write(json.dumps(rec,ensure_ascii=True)+"\n")

def write_csv(path,data):
    if not data:
        path.write_text("",encoding="utf-8")
        return
    with open(path,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)

write_csv(CODE_MATRIX,rows)
write_csv(READY,ready)
write_csv(NEEDS,needs)

by_tier={}
by_status={}
for r in rows:
    by_tier[r["tier"]]=by_tier.get(r["tier"],0)+1
    by_status[r["status"]]=by_status.get(r["status"],0)+1

summary={
    "mission":MISSION,
    "timestamp":now(),
    "input_matrix":str(MATRIX),
    "code_candidates_filtered":len(rows),
    "ready_for_staging_test":len(ready),
    "needs_review":len(needs),
    "by_tier":by_tier,
    "by_status":by_status,
    "code_matrix":str(CODE_MATRIX),
    "ready_csv":str(READY),
    "needs_csv":str(NEEDS),
    "ledger":str(LEDGER),
    "excluded":"INGEST CONTROL EVIDENCE REPORT LEDGER NODE_MODULES VENV SITE_PACKAGES CACHE",
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "next":"P4.91L2_STAGING_COPY_AND_TEST",
    "certification":"CODE_RECOVERY_ENGINE_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")

print(json.dumps(summary,indent=2,ensure_ascii=True))
