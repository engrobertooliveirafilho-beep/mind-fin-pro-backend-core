import csv, json, subprocess, hashlib, time, re, ast
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91M_ONE_BY_ONE_DEEP_DISSECTION"
ROOT=Path(r"_evidence\P4.91M_ONE_BY_ONE_DEEP_DISSECTION_20260623_175227")
READY=Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P4.91L_CODE_RECOVERY_ENGINE_20260623_170102\reports\runtime_test_candidates.csv")
ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

STAGING=ROOT/"staging"
LEDGER=ROOT/"ledger"/"processed_once.jsonl"
RESULTS=ROOT/"exports"/"deep_dissection_results.jsonl"
MATRIX=ROOT/"reports"/"deep_dissection_matrix.csv"
SUMMARY=ROOT/"reports"/"summary.json"

MAX_FILES=100
SLEEP_BETWEEN_FILES=15
COPY_TIMEOUT=120
MAX_BYTES=1200000

def now(): return datetime.now(timezone.utc).isoformat()
def sha(x): return hashlib.sha256(str(x).encode("utf-8","ignore")).hexdigest()
def safe(s): return re.sub(r"[^A-Za-z0-9_.-]+","_",s)[-150:]

def append(p,o):
    with open(p,"a",encoding="utf-8") as f:
        f.write(json.dumps(o,ensure_ascii=True)+"\n")

def done_keys():
    if not LEDGER.exists(): return set()
    out=set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try: out.add(json.loads(line)["key"])
        except: pass
    return out

def load_targets():
    rows=[]
    with open(READY,encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            if r.get("status")=="READY_FOR_STAGING_TEST":
                rows.append(r)
    return rows

def copy_one(path):
    local=STAGING/(sha(path)+"_"+safe(Path(path).name))
    if local.exists():
        return local,None

    cmd=[
        "rclone","copyto","gdrive:"+path,str(local),
        "--drive-root-folder-id",ROOT_ID,
        "--retries","1",
        "--low-level-retries","1",
        "--transfers","1",
        "--checkers","1",
        "--tpslimit","0.3",
        "--tpslimit-burst","1"
    ]

    try:
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=COPY_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None,"COPY_TIMEOUT"
    except Exception as e:
        return None,"COPY_EXCEPTION:"+str(e)

    if p.returncode != 0:
        return None,(p.stderr or b"").decode("utf-8","replace")[-2000:]

    if not local.exists():
        return None,"LOCAL_FILE_NOT_CREATED"

    return local,None

def read_file(local):
    data=local.read_bytes()
    if len(data)>MAX_BYTES:
        data=data[:MAX_BYTES]
    return data.decode("utf-8","replace")

def dissect(text,path):
    low=text.lower()
    ext=Path(path).suffix.lower()

    syntax="NOT_APPLICABLE"
    syntax_error=""
    if ext==".py":
        try:
            ast.parse(text)
            syntax="OK"
        except Exception as e:
            syntax="FAIL"; syntax_error=str(e)[:500]
    elif ext==".json":
        try:
            json.loads(text)
            syntax="OK"
        except Exception as e:
            syntax="FAIL"; syntax_error=str(e)[:500]

    deps=[]
    for k in ["fastapi","twilio","supabase","pgvector","openai","pandas","numpy","sqlalchemy","redis","celery","pytest"]:
        if k in low: deps.append(k)

    ideas=[]
    for k in ["memory","retrieval","rag","vector","agent","runtime","workflow","whatsapp","semantic","graph","context","knowledge","router","webhook"]:
        if k in low or k in path.lower(): ideas.append(k.upper())

    has_code=any(x in low for x in ["def ","class ","import ","function ","const ","router","fastapi"])
    has_tests=any(x in low for x in ["pytest","unittest","assert ","test_"])
    incomplete=any(x in low for x in ["todo","fixme","placeholder","not implemented","pending"])
    risky=any(x in low for x in ["delete(","shutil.rmtree","drop table","rm -rf","remove-item"])

    if risky:
        status="SECURITY_REVIEW"
    elif syntax=="FAIL":
        status="NEEDS_SYNTAX_FIX"
    elif incomplete:
        status="NEEDS_COMPLETION"
    elif has_code and has_tests:
        status="READY_TO_TEST"
    elif has_code:
        status="READY_NEEDS_TESTS"
    else:
        status="KNOWLEDGE_ONLY"

    return {
        "syntax":syntax,
        "syntax_error":syntax_error,
        "dependencies":"|".join(sorted(set(deps))),
        "ideas":"|".join(sorted(set(ideas))),
        "has_code":has_code,
        "has_tests":has_tests,
        "incomplete":incomplete,
        "risky":risky,
        "deep_status":status
    }

targets=load_targets()
done=done_keys()
rows=[]
processed=0
copied=0
failed=0

for r in targets:
    if processed >= MAX_FILES:
        break

    path=r["path"]
    key=sha(path+"|"+r.get("drive_id",""))

    if key in done:
        continue

    print("")
    print("="*100)
    print("DISSECTING_ONE_BY_ONE")
    print("PATH:", path)
    print("PROCESSED:", processed)
    print("="*100)

    local,err=copy_one(path)

    if err:
        rec={
            "key":key,
            "path":path,
            "status":"COPY_FAILED",
            "error":err,
            "processed_at":now(),
            "original_modified":False
        }
        append(RESULTS,rec)
        append(LEDGER,rec)
        rows.append(rec)
        failed+=1
        processed+=1
        time.sleep(SLEEP_BETWEEN_FILES)
        continue

    text=read_file(local)
    d=dissect(text,path)

    rec={
        "key":key,
        "path":path,
        "drive_id":r.get("drive_id"),
        "local_staging":str(local),
        "tier":r.get("tier"),
        "score":r.get("score"),
        "code_score":r.get("code_score"),
        "categories":r.get("categories"),
        "bytes_read":len(text.encode("utf-8","ignore")),
        "content_hash":sha(text),
        **d,
        "processed_at":now(),
        "original_modified":False
    }

    append(RESULTS,rec)
    append(LEDGER,rec)
    rows.append(rec)

    copied+=1
    processed+=1

    print("STATUS:", rec["deep_status"])
    print("SYNTAX:", rec["syntax"])
    print("DEPS:", rec["dependencies"])
    print("IDEAS:", rec["ideas"])

    time.sleep(SLEEP_BETWEEN_FILES)

if rows:
    with open(MATRIX,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
else:
    MATRIX.write_text("",encoding="utf-8")

summary={
    "mission":MISSION,
    "timestamp":now(),
    "source":str(READY),
    "max_files":MAX_FILES,
    "processed":processed,
    "copied_and_dissected":copied,
    "failed":failed,
    "matrix":str(MATRIX),
    "ledger":str(LEDGER),
    "results":str(RESULTS),
    "sleep_between_files_seconds":SLEEP_BETWEEN_FILES,
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "certification":"ONE_BY_ONE_DEEP_DISSECTION_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
print(json.dumps(summary,indent=2,ensure_ascii=True))
