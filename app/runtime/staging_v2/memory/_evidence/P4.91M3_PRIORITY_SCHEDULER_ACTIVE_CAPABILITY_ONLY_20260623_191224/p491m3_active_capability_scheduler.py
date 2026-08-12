import csv, json, hashlib, time, subprocess, re, ast
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91M3_PRIORITY_SCHEDULER_ACTIVE_CAPABILITY_ONLY"
ROOT=Path(r"_evidence\P4.91M3_PRIORITY_SCHEDULER_ACTIVE_CAPABILITY_ONLY_20260623_191224")
MATRIX=Path(r"_evidence\P4.91H_TO_O_PARALLEL_CAPABILITY_MATRIX_20260623_092058\reports\capability_matrix.csv")
ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"

STAGING=ROOT/"staging"
LEDGER=ROOT/"ledger"/"processed_ledger.jsonl"
RESULTS=ROOT/"exports"/"scheduler_results.jsonl"
FINAL_MATRIX=ROOT/"reports"/"priority_final_matrix.csv"
SUMMARY=ROOT/"reports"/"summary.json"
CERT=ROOT/"P4.91M3_CERTIFICATION.txt"

MAX_TOTAL=300
SLEEP_SECONDS=12
COPY_TIMEOUT=120
MAX_BYTES=1200000

ABSOLUTE_ARCHIVE=[
 "mind_evidence","_evidence","/evidence/","_control/","control/",
 "_drive_recovered","/reports/","reports/","report",
 "audit","auditoria","ledger","snapshot","final_truth"
]

VENDOR=[
 "node_modules","modulo node","@babel","@jest","metro-runtime","react-native",
 "regenerator-runtime","core-js","babel-runtime","vendor","third_party",
 "dist/","/dist","build/","/build","generated","polyfill",
 "site-packages","__pycache__",".venv","venv/",".pytest_cache",
 ".cache","coverage","dist-info","egg-info","license","licenses",
 "mind_v2_kb_zips_processed","/ingest/"
]

HIGH_VALUE=[
 "mind","eldora","neura","memory","retrieval","vector","embedding",
 "semantic","knowledge","context","agent","runtime","workflow",
 "orchestrator","supabase","pgvector","whatsapp","twilio","fastapi",
 "webhook","router","classifier","extractor"
]

ALLOWED_EXT=[
 ".py",".ps1",".js",".ts",".tsx",".jsx",".sql",".json",
 ".yaml",".yml",".md",".txt",".mq5",".mq4"
]

state={
 "started":time.time(),
 "processed":0,
 "score5":0,
 "score4":0,
 "score3":0,
 "archived":0,
 "vendor_archived":0,
 "ready_runtime":0,
 "ready_test":0,
 "needs_fix":0,
 "copy_failed":0,
 "last_score":"",
 "last_relevance":"",
 "last_path":"",
 "last_status":""
}

def now(): return datetime.now(timezone.utc).isoformat()
def sha(x): return hashlib.sha256(str(x).encode("utf-8","ignore")).hexdigest()
def safe(s): return re.sub(r"[^A-Za-z0-9_.-]+","_",s)[-160:]

def append(path,obj):
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj,ensure_ascii=True)+"\n")

def load_done():
    done=set()
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            try: done.add(json.loads(line).get("key"))
            except: pass
    return done

def is_absolute_archive(path):
    p=(path or "").lower()
    return any(x in p for x in ABSOLUTE_ARCHIVE)

def is_vendor(path):
    p=(path or "").lower()
    return any(x in p for x in VENDOR)

def relevance(path,categories,ideas):
    p=(path or "").lower()
    c=(categories or "").lower()
    i=(ideas or "").lower()

    if is_absolute_archive(path):
        return -999
    if is_vendor(path):
        return -500

    s=0
    for h in HIGH_VALUE:
        if h in p: s += 100
        if h in c: s += 50
        if h in i: s += 25

    if "/app/" in p or "/src/" in p or "/services/" in p or "/runtime/" in p:
        s += 200
    if p.endswith(".py"):
        s += 100
    if p.endswith(".ps1") or p.endswith(".sql"):
        s += 60

    return s

def load_matrix():
    rows=[]
    with open(MATRIX,encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            path=r.get("path","")
            if not path: continue
            p=path.lower()
            ext=Path(p).suffix.lower()

            if ext not in ALLOWED_EXT: continue
            if r.get("kind")=="ZIP": continue

            try: score=int(r.get("score") or 0)
            except: score=0

            try: code_score=int(r.get("code_score") or 0)
            except: code_score=0

            rel=relevance(path,r.get("categories",""),r.get("ideas",""))

            if rel < 100 and score < 4:
                continue

            r["_score_int"]=score
            r["_code_score_int"]=code_score
            r["_relevance"]=rel
            r["_archive"]=is_absolute_archive(path)
            r["_vendor"]=is_vendor(path)
            r["_key"]=sha(path+"|"+r.get("drive_id","")+"|"+r.get("size",""))
            rows.append(r)
    return rows

def pick_next(rows,done):
    for score in [5,4,3,2,1,0]:
        candidates=[
            r for r in rows
            if r["_score_int"]==score
            and r["_key"] not in done
            and not r["_archive"]
            and not r["_vendor"]
            and r["_relevance"] >= 100
        ]
        if candidates:
            candidates.sort(key=lambda x:(-x["_relevance"],-x["_code_score_int"],x.get("path","")))
            return candidates[0]

    archive=[
        r for r in rows
        if r["_key"] not in done
        and (r["_archive"] or r["_vendor"])
    ]
    if archive:
        archive.sort(key=lambda x:(-x["_score_int"],x.get("path","")))
        return archive[0]

    return None

def copy_file(path):
    local=STAGING/(sha(path)+"_"+safe(Path(path).name))
    if local.exists(): return local,None

    cmd=[
        "rclone","copyto","gdrive:"+path,str(local),
        "--drive-root-folder-id",ROOT_ID,
        "--retries","1","--low-level-retries","1",
        "--transfers","1","--checkers","1",
        "--tpslimit","0.25","--tpslimit-burst","1"
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

def dissect(text,path):
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
            syntax="FAIL"; syntax_error=str(e)[:500]
    elif ext==".json":
        try:
            json.loads(text)
            syntax="OK"
        except Exception as e:
            syntax="FAIL"; syntax_error=str(e)[:500]

    deps=[]
    for k in ["fastapi","uvicorn","pydantic","requests","httpx","supabase","psycopg","pgvector","openai","twilio","pandas","numpy","sqlalchemy","pytest","redis","celery"]:
        if k in low: deps.append(k)

    ideas=[]
    for k in HIGH_VALUE:
        if k in low or k in p: ideas.append(k.upper())

    has_code=any(x in low for x in ["def ","class ","import ","from ","function ","const ","let ","async ","await ","router","fastapi"])
    has_tests=any(x in low for x in ["pytest","unittest","assert ","test_","describe(","it("])
    runtime=any(x in low or x in p for x in ["fastapi","router","webhook","runtime","worker","twilio","supabase","pgvector"])
    capability=any(x in low or x in p for x in ["memory","retrieval","rag","vector","semantic","agent","orchestrator","workflow","context"])
    incomplete=any(x in low or x in p for x in ["todo","fixme","not implemented","placeholder","pending","incomplete","failed","abort","partial"])
    outdated=any(x in low or x in p for x in ["deprecated","obsolete","legacy","legado","old","quarentena"])
    risky=any(x in low for x in ["delete(","shutil.rmtree","drop table","remove-item","rm -rf"])

    if outdated: final_status="OUTDATED"
    elif risky: final_status="NEEDS_FIX"
    elif syntax=="FAIL": final_status="NEEDS_FIX"
    elif incomplete: final_status="NEEDS_COMPLETION"
    elif runtime and has_code: final_status="READY_FOR_RUNTIME"
    elif capability and has_code: final_status="READY_FOR_CAPABILITY_TEST"
    elif has_code: final_status="READY_FOR_STAGING_TEST"
    else: final_status="ARCHIVE_ONLY"

    if final_status=="READY_FOR_RUNTIME":
        next_action="TEST_IN_RUNTIME_STAGING"; priority="P1"
    elif final_status=="READY_FOR_CAPABILITY_TEST":
        next_action="TEST_CAPABILITY_ISOLATED"; priority="P2"
    elif final_status=="READY_FOR_STAGING_TEST":
        next_action="CODE_REVIEW_AND_TEST"; priority="P3"
    elif final_status in ["NEEDS_FIX","NEEDS_COMPLETION"]:
        next_action="FIX_OR_COMPLETE_BEFORE_TEST"; priority="P4"
    else:
        next_action="NO_IMMEDIATE_INTEGRATION"; priority="P9"

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
        "risky":risky,
        "final_status":final_status,
        "next_action":next_action,
        "integration_priority":priority,
        "certified":True
    }

def update_counts(score,status,arch=False,vendor=False):
    state["processed"]+=1
    if score==5: state["score5"]+=1
    elif score==4: state["score4"]+=1
    elif score==3: state["score3"]+=1
    if arch: state["archived"]+=1
    if vendor: state["vendor_archived"]+=1
    if status=="READY_FOR_RUNTIME": state["ready_runtime"]+=1
    if status in ["READY_FOR_STAGING_TEST","READY_FOR_CAPABILITY_TEST"]: state["ready_test"]+=1
    if status in ["NEEDS_FIX","NEEDS_COMPLETION"]: state["needs_fix"]+=1
    if status=="COPY_FAILED": state["copy_failed"]+=1

def print_monitor():
    e=int(time.time()-state["started"])
    print("")
    print("="*110)
    print("P4.91M3 ACTIVE CAPABILITY ONLY SCHEDULER")
    print("="*110)
    print(f"Elapsed............. {e//86400} dias {(e%86400)//3600:02d}:{(e%3600)//60:02d}:{e%60:02d}")
    print(f"Processed........... {state['processed']} / {MAX_TOTAL}")
    print(f"Score 5............. {state['score5']}")
    print(f"Score 4............. {state['score4']}")
    print(f"Score 3............. {state['score3']}")
    print(f"Archive Blocked..... {state['archived']}")
    print(f"Vendor Archived..... {state['vendor_archived']}")
    print(f"Ready Runtime....... {state['ready_runtime']}")
    print(f"Ready Test.......... {state['ready_test']}")
    print(f"Needs Fix........... {state['needs_fix']}")
    print(f"Copy Failed......... {state['copy_failed']}")
    print("-"*110)
    print(f"Last Score.......... {state['last_score']}")
    print(f"Last Relevance...... {state['last_relevance']}")
    print(f"Last Status......... {state['last_status']}")
    print(f"Last Path........... {state['last_path'][:100]}")
    print("="*110)

output=[]
while state["processed"] < MAX_TOTAL:
    rows=load_matrix()
    done=load_done()
    item=pick_next(rows,done)
    if not item: break

    started=now()
    path=item["path"]
    score=item["_score_int"]
    code_score=item["_code_score_int"]
    key=item["_key"]
    rel=item["_relevance"]

    state["last_score"]=score
    state["last_relevance"]=rel
    state["last_path"]=path
    state["last_status"]="PROCESSING"
    print_monitor()

    if item["_archive"] or item["_vendor"]:
        status="ARCHIVE_ONLY"
        action="IGNORE_EVIDENCE_OR_VENDOR_CODE" if item["_archive"] else "IGNORE_VENDOR_CODE"
        rec={
            "key":key,"mission":MISSION,"path":path,"drive_id":item.get("drive_id"),
            "score":score,"code_score":code_score,"capability_relevance":rel,
            "processing_started_at":started,"processing_finished_at":now(),
            "processing_status":"COMPLETE","final_status":status,
            "next_action":action,"integration_priority":"P99",
            "processed_once":True,"reprocess_required":False,
            "original_modified":False,"certified":True
        }
        append(RESULTS,rec); append(LEDGER,rec); output.append(rec)
        update_counts(score,status,item["_archive"],item["_vendor"])
        state["last_status"]=status
        time.sleep(1)
        continue

    local,err=copy_file(path)
    if err:
        rec={
            "key":key,"mission":MISSION,"path":path,"drive_id":item.get("drive_id"),
            "score":score,"code_score":code_score,"capability_relevance":rel,
            "processing_started_at":started,"processing_finished_at":now(),
            "processing_status":"COMPLETE","final_status":"COPY_FAILED",
            "next_action":"RETRY_LATER_WITH_QUOTA_SAFE_MODE",
            "reprocess_required":True,"error":err,
            "original_modified":False,"certified":True
        }
        append(RESULTS,rec); append(LEDGER,rec); output.append(rec)
        update_counts(score,"COPY_FAILED")
        state["last_status"]="COPY_FAILED"
        time.sleep(SLEEP_SECONDS)
        continue

    text=read_text(local)
    d=dissect(text,path)
    rec={
        "key":key,"mission":MISSION,"path":path,"drive_id":item.get("drive_id"),
        "local_staging":str(local),"score":score,"code_score":code_score,
        "capability_relevance":rel,"categories":item.get("categories"),
        "processing_started_at":started,"processing_finished_at":now(),
        "processing_status":"COMPLETE","processed_once":True,
        "reprocess_required":False,"bytes_read":len(text.encode("utf-8","ignore")),
        "content_hash":sha(text),**d,"original_modified":False
    }
    append(RESULTS,rec); append(LEDGER,rec); output.append(rec)
    update_counts(score,rec["final_status"])
    state["last_status"]=rec["final_status"]
    time.sleep(SLEEP_SECONDS)

if output:
    fields=sorted(set().union(*[r.keys() for r in output]))
    with open(FINAL_MATRIX,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        w.writerows(output)
else:
    FINAL_MATRIX.write_text("",encoding="utf-8")

summary={
    "mission":MISSION,
    "timestamp":now(),
    "processed":state["processed"],
    "score5_processed":state["score5"],
    "score4_processed":state["score4"],
    "score3_processed":state["score3"],
    "archive_blocked":state["archived"],
    "vendor_archived":state["vendor_archived"],
    "ready_runtime":state["ready_runtime"],
    "ready_test":state["ready_test"],
    "needs_fix":state["needs_fix"],
    "copy_failed":state["copy_failed"],
    "final_matrix":str(FINAL_MATRIX),
    "ledger":str(LEDGER),
    "results":str(RESULTS),
    "scheduler_rule":"SCORE_5_FIRST_ACTIVE_CAPABILITY_ONLY; EVIDENCE_CONTROL_VENDOR_ARCHIVED_WITHOUT_COPY",
    "original_modified":False,
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "certification":"ACTIVE_CAPABILITY_ONLY_SCHEDULER_CERTIFIED"
}

SUMMARY.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
print(json.dumps(summary,indent=2,ensure_ascii=True))
