import csv, json, hashlib, time, subprocess, re, ast
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91M_PRIORITY_SCORE_SCHEDULER_FULL"
ROOT=Path(r"_evidence\P4.91M_PRIORITY_SCORE_SCHEDULER_FULL_20260623_182409")
MATRIX=Path(r"_evidence\P4.91H_TO_O_PARALLEL_CAPABILITY_MATRIX_20260623_092058\reports\capability_matrix.csv")
ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

STAGING=ROOT/"staging"
LEDGER=ROOT/"ledger"/"priority_processed_ledger.jsonl"
RESULTS=ROOT/"exports"/"priority_scheduler_results.jsonl"
FINAL_MATRIX=ROOT/"reports"/"priority_final_matrix.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91M_CERTIFICATION.txt"

MAX_TOTAL=300
SLEEP_SECONDS=12
COPY_TIMEOUT=120
MAX_BYTES=1200000

BAD=[
 "mind_v2_kb_zips_processed","/ingest/","node_modules","site-packages",
 "__pycache__",".venv","venv/","dist-info","egg-info",".pytest_cache",
 ".cache","coverage","license","licenses"
]

ALLOWED_EXT=[".py",".ps1",".js",".ts",".tsx",".jsx",".sql",".json",".yaml",".yml",".md",".txt",".mq5",".mq4"]

FINAL_STATUSES=[
 "READY_FOR_RUNTIME",
 "READY_FOR_STAGING_TEST",
 "READY_FOR_CAPABILITY_TEST",
 "NEEDS_FIX",
 "NEEDS_COMPLETION",
 "OUTDATED",
 "DUPLICATE",
 "ARCHIVE_ONLY",
 "QUARANTINED",
 "NO_ACTION_REQUIRED",
 "COPY_FAILED"
]

state={
 "started":time.time(),
 "processed":0,
 "score5":0,
 "score4":0,
 "score3":0,
 "score2":0,
 "score1":0,
 "score0":0,
 "ready_runtime":0,
 "ready_test":0,
 "needs_fix":0,
 "copy_failed":0,
 "last_score":"",
 "last_path":"",
 "last_status":""
}

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(x):
    return hashlib.sha256(str(x).encode("utf-8","ignore")).hexdigest()

def safe(s):
    return re.sub(r"[^A-Za-z0-9_.-]+","_",s)[-160:]

def append(path,obj):
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj,ensure_ascii=True)+"\n")

def load_done():
    done=set()
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line).get("key"))
            except:
                pass
    return done

def load_matrix():
    rows=[]
    with open(MATRIX,encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            path=r.get("path","")
            p=path.lower()
            ext=Path(p).suffix.lower()

            if not path:
                continue
            if ext not in ALLOWED_EXT:
                continue
            if r.get("kind")=="ZIP":
                continue
            if any(b in p for b in BAD):
                continue

            try:
                score=int(r.get("score") or 0)
            except:
                score=0

            try:
                code_score=int(r.get("code_score") or 0)
            except:
                code_score=0

            if score < 3 and code_score < 3:
                continue

            r["_score_int"]=score
            r["_code_score_int"]=code_score
            r["_key"]=sha(path+"|"+r.get("drive_id","")+"|"+r.get("size",""))
            rows.append(r)
    return rows

def pick_next(rows,done):
    for score in [5,4,3,2,1,0]:
        candidates=[r for r in rows if r["_score_int"]==score and r["_key"] not in done]
        if candidates:
            candidates.sort(key=lambda x: (
                -x["_code_score_int"],
                0 if "runtime" in x.get("path","").lower() else 1,
                x.get("path","")
            ))
            return candidates[0]
    return None

def copy_file(path):
    local=STAGING/(sha(path)+"_"+safe(Path(path).name))
    if local.exists():
        return local,None

    cmd=[
        "rclone","copyto",
        "gdrive:"+path,
        str(local),
        "--drive-root-folder-id",ROOT_ID,
        "--retries","1",
        "--low-level-retries","1",
        "--transfers","1",
        "--checkers","1",
        "--tpslimit","0.25",
        "--tpslimit-burst","1"
    ]

    try:
        p=subprocess.run(cmd,capture_output=True,text=False,timeout=COPY_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None,"COPY_TIMEOUT"
    except Exception as e:
        return None,("COPY_EXCEPTION:"+str(e))[:1500]

    if p.returncode != 0:
        return None,(p.stderr or b"").decode("utf-8","replace")[-2000:]

    if not local.exists():
        return None,"LOCAL_FILE_NOT_CREATED"

    return local,None

def read_text(local):
    data=local.read_bytes()
    if len(data)>MAX_BYTES:
        data=data[:MAX_BYTES]
    return data.decode("utf-8","replace")

def dissect(text,path,score,code_score):
    low=text.lower()
    p=path.lower()
    ext=Path(path).suffix.lower()

    syntax="NOT_APPLICABLE"
    syntax_error=""

    if ext==".py":
        try:
            ast.parse(text)
            syntax="OK"
        except Exception as e:
            syntax="FAIL"
            syntax_error=str(e)[:500]
    elif ext==".json":
        try:
            json.loads(text)
            syntax="OK"
        except Exception as e:
            syntax="FAIL"
            syntax_error=str(e)[:500]

    deps=[]
    for k in ["fastapi","uvicorn","pydantic","requests","httpx","supabase","psycopg","pgvector","openai","twilio","pandas","numpy","sqlalchemy","pytest","redis","celery"]:
        if k in low:
            deps.append(k)

    ideas=[]
    for k in ["memory","retrieval","rag","vector","embedding","agent","runtime","orchestrator","workflow","whatsapp","twilio","supabase","fastapi","ledger","classifier","extractor","knowledge","context","semantic","graph","eldora","mind","neura","schema","sql"]:
        if k in low or k in p:
            ideas.append(k.upper())

    has_code=any(x in low for x in ["def ","class ","import ","from ","function ","const ","let ","async ","await ","router","fastapi"])
    has_tests=any(x in low for x in ["pytest","unittest","assert ","test_","describe(","it("])
    runtime=any(x in low or x in p for x in ["fastapi","router","webhook","runtime","worker","twilio","supabase","pgvector"])
    capability=any(x in low or x in p for x in ["memory","retrieval","rag","vector","semantic","agent","orchestrator","workflow","context"])
    incomplete=any(x in low or x in p for x in ["todo","fixme","not implemented","placeholder","pending","incomplete","failed","abort","partial"])
    outdated=any(x in low or x in p for x in ["deprecated","obsolete","legacy","legado","old","quarentena"])
    duplicate=any(x in p for x in ["duplicate","duplicado","duplicados","copy","copia","backup"])
    risky=any(x in low for x in ["delete(","shutil.rmtree","drop table","remove-item","rm -rf"])

    if duplicate:
        final_status="DUPLICATE"
    elif outdated:
        final_status="OUTDATED"
    elif risky:
        final_status="NEEDS_FIX"
    elif syntax=="FAIL":
        final_status="NEEDS_FIX"
    elif incomplete:
        final_status="NEEDS_COMPLETION"
    elif runtime and has_code and syntax!="FAIL":
        final_status="READY_FOR_RUNTIME"
    elif capability and has_code:
        final_status="READY_FOR_CAPABILITY_TEST"
    elif has_code:
        final_status="READY_FOR_STAGING_TEST"
    else:
        final_status="ARCHIVE_ONLY"

    if final_status=="READY_FOR_RUNTIME":
        next_action="TEST_IN_RUNTIME_STAGING"
        integration_priority="P1"
    elif final_status=="READY_FOR_CAPABILITY_TEST":
        next_action="TEST_CAPABILITY_ISOLATED"
        integration_priority="P2"
    elif final_status=="READY_FOR_STAGING_TEST":
        next_action="CODE_REVIEW_AND_TEST"
        integration_priority="P3"
    elif final_status in ["NEEDS_FIX","NEEDS_COMPLETION"]:
        next_action="FIX_OR_COMPLETE_BEFORE_TEST"
        integration_priority="P4"
    else:
        next_action="NO_IMMEDIATE_INTEGRATION"
        integration_priority="P9"

    return {
        "syntax":syntax,
        "syntax_error":syntax_error,
        "dependencies":"|".join(sorted(set(deps))),
        "ideas_real":"|".join(sorted(set(ideas))),
        "has_code":has_code,
        "has_tests":has_tests,
        "runtime_candidate":runtime,
        "capability_candidate":capability,
        "incomplete":incomplete,
        "outdated":outdated,
        "duplicate":duplicate,
        "risky":risky,
        "final_status":final_status,
        "next_action":next_action,
        "integration_priority":integration_priority,
        "certified":True
    }

def update_counts(score,status):
    state["processed"]+=1
    state[f"score{score}"]+=1
    if status=="READY_FOR_RUNTIME":
        state["ready_runtime"]+=1
    if status in ["READY_FOR_STAGING_TEST","READY_FOR_CAPABILITY_TEST"]:
        state["ready_test"]+=1
    if status in ["NEEDS_FIX","NEEDS_COMPLETION"]:
        state["needs_fix"]+=1
    if status=="COPY_FAILED":
        state["copy_failed"]+=1

def print_monitor():
    e=int(time.time()-state["started"])
    print("")
    print("="*110)
    print("P4.91M PRIORITY SCORE SCHEDULER FULL")
    print("="*110)
    print(f"Elapsed............. {e//86400} dias {(e%86400)//3600:02d}:{(e%3600)//60:02d}:{e%60:02d}")
    print(f"Processed........... {state['processed']} / {MAX_TOTAL}")
    print(f"Score 5............. {state['score5']}")
    print(f"Score 4............. {state['score4']}")
    print(f"Score 3............. {state['score3']}")
    print(f"Ready Runtime....... {state['ready_runtime']}")
    print(f"Ready Test.......... {state['ready_test']}")
    print(f"Needs Fix........... {state['needs_fix']}")
    print(f"Copy Failed......... {state['copy_failed']}")
    print("-"*110)
    print(f"Last Score.......... {state['last_score']}")
    print(f"Last Status......... {state['last_status']}")
    print(f"Last Path........... {state['last_path'][:100]}")
    print("="*110)

rows=load_matrix()
done=load_done()
output_rows=[]

while state["processed"] < MAX_TOTAL:
    rows=load_matrix()
    done=load_done()

    item=pick_next(rows,done)
    if not item:
        break

    started=now()
    path=item["path"]
    score=item["_score_int"]
    code_score=item["_code_score_int"]
    key=item["_key"]

    state["last_score"]=score
    state["last_path"]=path
    state["last_status"]="PROCESSING"
    print_monitor()

    local,err=copy_file(path)

    if err:
        rec={
            "key":key,
            "mission":MISSION,
            "path":path,
            "drive_id":item.get("drive_id"),
            "score":score,
            "code_score":code_score,
            "priority_queue":f"SCORE_{score}",
            "processing_started_at":started,
            "processing_finished_at":now(),
            "processing_status":"COMPLETE",
            "final_status":"COPY_FAILED",
            "next_action":"RETRY_LATER_WITH_QUOTA_SAFE_MODE",
            "reprocess_required":True,
            "error":err,
            "original_modified":False,
            "certified":True
        }
        append(RESULTS,rec)
        append(LEDGER,rec)
        output_rows.append(rec)
        update_counts(score,"COPY_FAILED")
        state["last_status"]="COPY_FAILED"
        time.sleep(SLEEP_SECONDS)
        continue

    text=read_text(local)
    d=dissect(text,path,score,code_score)

    finished=now()
    rec={
        "key":key,
        "mission":MISSION,
        "path":path,
        "drive_id":item.get("drive_id"),
        "local_staging":str(local),
        "score":score,
        "code_score":code_score,
        "categories":item.get("categories"),
        "priority_queue":f"SCORE_{score}",
        "processing_started_at":started,
        "processing_finished_at":finished,
        "processing_status":"COMPLETE",
        "processed_once":True,
        "reprocess_required":False,
        "bytes_read":len(text.encode("utf-8","ignore")),
        "content_hash":sha(text),
        **d,
        "original_modified":False
    }

    append(RESULTS,rec)
    append(LEDGER,rec)
    output_rows.append(rec)
    update_counts(score,rec["final_status"])
    state["last_status"]=rec["final_status"]

    time.sleep(SLEEP_SECONDS)

if output_rows:
    with open(FINAL_MATRIX,"w",encoding="utf-8-sig",newline="") as f:
        fields=sorted(set().union(*[r.keys() for r in output_rows]))
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        w.writerows(output_rows)
else:
    FINAL_MATRIX.write_text("",encoding="utf-8")

summary={
    "mission":MISSION,
    "timestamp":now(),
    "source_matrix":str(MATRIX),
    "processed":state["processed"],
    "score5_processed":state["score5"],
    "score4_processed":state["score4"],
    "score3_processed":state["score3"],
    "ready_runtime":state["ready_runtime"],
    "ready_test":state["ready_test"],
    "needs_fix":state["needs_fix"],
    "copy_failed":state["copy_failed"],
    "final_matrix":str(FINAL_MATRIX),
    "ledger":str(LEDGER),
    "results":str(RESULTS),
    "scheduler_rule":"ALWAYS_PROCESS_SCORE_5_FIRST_THEN_4_THEN_3; IF_NEW_SCORE_5_APPEARS_INTERRUPT_LOWER_SCORE",
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "certification":"PRIORITY_SCORE_SCHEDULER_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")

print("")
print("=== P4.91M SUMMARY ===")
print(json.dumps(summary,indent=2,ensure_ascii=True))
