import json, time, subprocess
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91F4_MIND_ONLY_LOCKED_WALK"
ROOT_ID="1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A"
REMOTE="gdrive:"
OUT=Path(r"_evidence\P4.91F4_MIND_ONLY_LOCKED_WALK_20260622_125928")
STATE=OUT/"state"
EXPORTS=OUT/"exports"

QUEUE=STATE/"queue.jsonl"
DONE=STATE/"done.jsonl"
ERRORS=STATE/"errors.jsonl"
ITEMS=EXPORTS/"mind_items.jsonl"
FILES=EXPORTS/"mind_files.jsonl"
FOLDERS=EXPORTS/"mind_folders.jsonl"
ZIPS=EXPORTS/"mind_zips.jsonl"
SNAP=OUT/"P4.91F4_MIND_ONLY_LOCKED_SNAPSHOT.json"

for p in [QUEUE,DONE,ERRORS,ITEMS,FILES,FOLDERS,ZIPS]:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)

def now():
    return datetime.now(timezone.utc).isoformat()

def write(path,obj):
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj,ensure_ascii=True)+"\n")

def lines(path):
    return sum(1 for _ in open(path,encoding="utf-8")) if path.exists() else 0

def done_set():
    out=set()
    for line in DONE.read_text(encoding="utf-8").splitlines():
        try: out.add(json.loads(line).get("path",""))
        except: pass
    return out

def queue_items():
    out=[]
    for line in QUEUE.read_text(encoding="utf-8").splitlines():
        try: out.append(json.loads(line))
        except: pass
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

def lsjson(folder):
    target=REMOTE + folder if folder else REMOTE
    cmd=[
        "rclone","lsjson",target,
        "--drive-root-folder-id",ROOT_ID,
        "--max-depth","1",
        "--no-mimetype"
    ]
    t0=time.time()
    p=subprocess.run(cmd,capture_output=True,text=False,timeout=900)
    elapsed=round(time.time()-t0,3)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or b"").decode("utf-8","replace")[-4000:])
    raw=(p.stdout or b"[]").decode("utf-8","replace")
    return json.loads(raw or "[]"), elapsed

if QUEUE.stat().st_size == 0:
    write(QUEUE,{"path":"","depth":0,"queued_at":now()})

started=time.time()
done=done_set()

while True:
    pending=[x for x in queue_items() if x.get("path","") not in done]
    if not pending:
        break

    cur=pending[0]
    folder=cur.get("path","")
    depth=cur.get("depth",0)

    try:
        rows,elapsed=lsjson(folder)

        for r in rows:
            name=r.get("Name","")
            isdir=bool(r.get("IsDir"))
            full=child(folder,name)
            rec={
                "mission":MISSION,
                "scope":"MIND_FOLDER_ONLY",
                "root_folder_id":ROOT_ID,
                "scanned_at":now(),
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
            write(ITEMS,rec)
            if isdir:
                write(FOLDERS,rec)
                write(QUEUE,{"path":full,"depth":depth+1,"queued_at":now()})
            else:
                write(FILES,rec)
                if rec["kind"]=="ZIP":
                    write(ZIPS,rec)

        write(DONE,{
            "path":folder,
            "depth":depth,
            "children":len(rows),
            "elapsed_seconds":elapsed,
            "done_at":now()
        })
        done.add(folder)

        print(f"[MIND_ONLY] done={lines(DONE)} queue={lines(QUEUE)} files={lines(FILES)} folders={lines(FOLDERS)} zips={lines(ZIPS)} last={folder}",flush=True)

    except Exception as e:
        write(ERRORS,{
            "path":folder,
            "depth":depth,
            "error":str(e)[:4000],
            "error_at":now()
        })
        write(DONE,{"path":folder,"depth":depth,"status":"ERROR_LOGGED","done_at":now()})
        done.add(folder)

queue_total=lines(QUEUE)
done_total=lines(DONE)
pending=max(queue_total-done_total,0)

snap={
    "mission":MISSION,
    "status":"MIND_FOLDER_ONLY_INDEX_CERTIFIED" if pending==0 else "PARTIAL",
    "scope":"ONLY_FOLDER_ID_1tVbi6243j7QFSdjAd6oIZ7IqEgLvYE-A",
    "root_folder_id":ROOT_ID,
    "queue_total":queue_total,
    "done_total":done_total,
    "pending_total":pending,
    "items_total":lines(ITEMS),
    "files_total":lines(FILES),
    "folders_total":lines(FOLDERS),
    "zip_files":lines(ZIPS),
    "errors_total":lines(ERRORS),
    "elapsed_seconds":round(time.time()-started,3),
    "delete":"FORBIDDEN",
    "move_original":"FORBIDDEN",
    "modify_original":"FORBIDDEN",
    "next":"P4.91G_DRIVE_ZIP_RECURSIVE_ABSORPTION"
}

SNAP.write_text(json.dumps(snap,indent=2,ensure_ascii=True),encoding="utf-8")
print(json.dumps(snap,indent=2,ensure_ascii=True))
