import json, time, subprocess
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91F4_MIND_FOLDER_ONLY_RESUMABLE_WALK"
REMOTE='gdrive,root_folder_id=1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A:'

OUT=Path(r"_evidence\P4.91F4_MIND_FOLDER_ONLY_RESUMABLE_WALK_20260622_124551")
STATE=OUT/"state"
EXPORTS=OUT/"exports"

QUEUE=STATE/"queue.jsonl"
DONE=STATE/"done.jsonl"
ERRORS=STATE/"errors.jsonl"
ITEMS=EXPORTS/"mind_drive_items.jsonl"
FILES=EXPORTS/"mind_drive_files.jsonl"
FOLDERS=EXPORTS/"mind_drive_folders.jsonl"
ZIPS=EXPORTS/"mind_drive_zips.jsonl"
SNAP=OUT/"P4.91F4_MIND_FOLDER_ONLY_SNAPSHOT.json"
CERT=OUT/"P4.91F4_MIND_FOLDER_ONLY_CERTIFICATION.txt"

for p in [QUEUE,DONE,ERRORS,ITEMS,FILES,FOLDERS,ZIPS]:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)

def now():
    return datetime.now(timezone.utc).isoformat()

def jwrite(path,obj):
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj,ensure_ascii=True)+"\n")

def read_done():
    s=set()
    for line in DONE.read_text(encoding="utf-8").splitlines():
        try:
            s.add(json.loads(line).get("path",""))
        except:
            pass
    return s

def seed():
    if QUEUE.stat().st_size == 0:
        jwrite(QUEUE,{"path":"","depth":0,"queued_at":now()})

def run_lsjson(folder):
    target = REMOTE + folder if folder else REMOTE
    cmd = ["rclone","lsjson",target,"--max-depth","1","--no-mimetype"]
    t0=time.time()
    p=subprocess.run(cmd,capture_output=True,text=False,timeout=900)
    elapsed=round(time.time()-t0,3)
    if p.returncode != 0:
        err=(p.stderr or b"").decode("utf-8","replace")[-4000:]
        raise RuntimeError(err)
    raw=(p.stdout or b"[]").decode("utf-8","replace")
    return json.loads(raw or "[]"), elapsed

def load_queue():
    out=[]
    for line in QUEUE.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except:
            pass
    return out

def child(parent,name):
    return (parent.rstrip("/")+"/"+name).strip("/") if parent else name.strip("/")

def kind(name):
    ext=Path(name).suffix.lower()
    if ext==".zip": return "ZIP"
    if ext in [".py",".ps1",".js",".ts",".tsx",".jsx",".sql",".mq5",".mq4",".yml",".yaml",".json",".jsonl",".toml",".ini",".env"]: return "CODE"
    if ext in [".md",".txt",".doc",".docx",".pdf",".rtf"]: return "DOC"
    if ext in [".csv",".xlsx",".xls",".parquet",".db",".sqlite"]: return "DATASET"
    return "OTHER"

def count_lines(p):
    return sum(1 for _ in open(p,encoding="utf-8")) if p.exists() else 0

seed()
started=time.time()
done=read_done()

while True:
    q=load_queue()
    pending=[x for x in q if x.get("path","") not in done]
    if not pending:
        break

    cur=pending[0]
    folder=cur.get("path","")
    depth=cur.get("depth",0)

    try:
        rows,elapsed=run_lsjson(folder)

        for r in rows:
            name=r.get("Name","")
            isdir=bool(r.get("IsDir"))
            full=child(folder,name)
            rec={
                "mission":MISSION,
                "scanned_at":now(),
                "root_folder_id":"1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A",
                "parent":folder,
                "path":full,
                "name":name,
                "is_dir":isdir,
                "size":r.get("Size"),
                "mod_time":r.get("ModTime"),
                "id":r.get("ID"),
                "kind":"FOLDER" if isdir else kind(name),
                "delete":"FORBIDDEN",
                "move_original":"FORBIDDEN",
                "modify_original":"FORBIDDEN"
            }
            jwrite(ITEMS,rec)
            if isdir:
                jwrite(FOLDERS,rec)
                jwrite(QUEUE,{"path":full,"depth":depth+1,"queued_at":now()})
            else:
                jwrite(FILES,rec)
                if rec["kind"]=="ZIP":
                    jwrite(ZIPS,rec)

        jwrite(DONE,{
            "path":folder,
            "depth":depth,
            "children":len(rows),
            "elapsed_seconds":elapsed,
            "done_at":now()
        })
        done.add(folder)

        if count_lines(DONE) % 50 == 0:
            print(f"[{MISSION}] done={count_lines(DONE)} queue={count_lines(QUEUE)} files={count_lines(FILES)} folders={count_lines(FOLDERS)} zips={count_lines(ZIPS)}",flush=True)

    except Exception as e:
        jwrite(ERRORS,{
            "path":folder,
            "depth":depth,
            "error":str(e)[:4000],
            "error_at":now()
        })
        jwrite(DONE,{
            "path":folder,
            "depth":depth,
            "status":"ERROR_LOGGED",
            "done_at":now()
        })
        done.add(folder)

queue=count_lines(QUEUE)
done_n=count_lines(DONE)
pending=max(queue-done_n,0)
snap={
    "mission":MISSION,
    "status":"MIND_FOLDER_ONLY_INDEX_CERTIFIED" if pending==0 else "PARTIAL_RESUMABLE",
    "timestamp":now(),
    "remote":REMOTE,
    "root_folder_id":"1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A",
    "queue_total":queue,
    "done_total":done_n,
    "pending_total":pending,
    "items_total":count_lines(ITEMS),
    "files_total":count_lines(FILES),
    "folders_total":count_lines(FOLDERS),
    "zip_files":count_lines(ZIPS),
    "errors_total":count_lines(ERRORS),
    "elapsed_seconds":round(time.time()-started,3),
    "scope":"MIND_FOLDER_ONLY",
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "next":"P4.91G_DRIVE_ZIP_RECURSIVE_ABSORPTION"
}
SNAP.write_text(json.dumps(snap,indent=2,ensure_ascii=True),encoding="utf-8")
CERT.write_text(json.dumps(snap,indent=2,ensure_ascii=True),encoding="utf-8")
print(json.dumps(snap,indent=2,ensure_ascii=True))
