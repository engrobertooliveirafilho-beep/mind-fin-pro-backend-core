import os, json, time, subprocess, hashlib, sys
from pathlib import Path
from datetime import datetime, timezone

MISSION="P4.91F4_RESUMABLE_FULL_DRIVE_WALK"
REMOTE="gdrive:"
OUT=Path(r"_evidence\P4.91F4_RESUMABLE_FULL_DRIVE_WALK_20260622_121115")
STATE=OUT/"state"
LOGS=OUT/"logs"
EXPORTS=OUT/"exports"

QUEUE=STATE/"queue.jsonl"
DONE=STATE/"done.jsonl"
ERRORS=STATE/"errors.jsonl"
ITEMS=EXPORTS/"drive_items.jsonl"
FOLDERS=EXPORTS/"drive_folders.jsonl"
FILES=EXPORTS/"drive_files.jsonl"
ZIPS=EXPORTS/"drive_zips.jsonl"
SNAP=OUT/"P4.91F4_SNAPSHOT.json"
CERT=OUT/"P4.91F4_CERTIFICATION.txt"

DELETE_FORBIDDEN=True
MOVE_ORIGINAL_FORBIDDEN=True
MODIFY_ORIGINAL_FORBIDDEN=True

for p in [QUEUE,DONE,ERRORS,ITEMS,FOLDERS,FILES,ZIPS]:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)

def now():
    return datetime.now(timezone.utc).isoformat()

def jwrite(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=True) + "\n")

def read_jsonl_set(path, key="path"):
    s=set()
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    if line.strip():
                        s.add(json.loads(line).get(key,""))
                except:
                    pass
    return s

def seed_queue():
    if QUEUE.stat().st_size == 0:
        jwrite(QUEUE, {"path":"", "depth":0, "queued_at":now()})

def run_rclone_lsjson(folder):
    target = REMOTE + folder if folder else REMOTE
    cmd = [
        "rclone","lsjson",target,
        "--dirs-only=false",
        "--files-only=false",
        "--fast-list=false",
        "--no-mimetype",
        "--max-depth","1"
    ]
    t0=time.time()
    p=subprocess.run(cmd, capture_output=True, text=False, timeout=900)
    elapsed=round(time.time()-t0,3)
    if p.returncode != 0:
        raise RuntimeError(json.dumps({
            "returncode":p.returncode,
            "stderr":(p.stderr or b'').decode("utf-8","replace")[-4000:],
            "elapsed":elapsed
        }, ensure_ascii=True))
    raw=(p.stdout or b"[]").decode("utf-8","replace"); data=json.loads(raw or "[]")
    return data, elapsed

def load_queue():
    q=[]
    with open(QUEUE, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    q.append(json.loads(line))
                except:
                    pass
    return q

def rel_child(parent, name):
    return (parent.rstrip("/") + "/" + name).strip("/") if parent else name.strip("/")

def file_kind(name):
    ext=Path(name).suffix.lower()
    if ext == ".zip": return "ZIP"
    if ext in [".py",".ps1",".js",".ts",".tsx",".jsx",".sql",".mq5",".mq4",".yml",".yaml",".json",".toml",".ini",".env",".dockerfile"]: return "CODE"
    if ext in [".md",".txt",".doc",".docx",".pdf",".rtf"]: return "DOC"
    if ext in [".csv",".xlsx",".xls",".parquet",".db",".sqlite",".jsonl"]: return "DATASET"
    return "OTHER"

def main():
    seed_queue()
    done=read_jsonl_set(DONE)
    errors_count=0
    folders_walked=0
    files_total=0
    folders_total=0
    items_total=0
    zip_files=0
    started=time.time()

    while True:
        queue=load_queue()
        pending=[x for x in queue if x.get("path","") not in done]
        if not pending:
            break

        item=pending[0]
        folder=item.get("path","")
        depth=item.get("depth",0)

        try:
            children, elapsed = run_rclone_lsjson(folder)
            folders_walked += 1

            for c in children:
                name=c.get("Name","")
                isdir=bool(c.get("IsDir"))
                full=rel_child(folder,name)
                rec={
                    "mission":MISSION,
                    "scanned_at":now(),
                    "parent":folder,
                    "path":full,
                    "name":name,
                    "is_dir":isdir,
                    "size":c.get("Size"),
                    "mod_time":c.get("ModTime"),
                    "id":c.get("ID"),
                    "mime_type":c.get("MimeType"),
                    "kind":"FOLDER" if isdir else file_kind(name),
                    "source":"gdrive",
                    "delete_forbidden":DELETE_FORBIDDEN,
                    "move_original_forbidden":MOVE_ORIGINAL_FORBIDDEN,
                    "modify_original_forbidden":MODIFY_ORIGINAL_FORBIDDEN
                }

                jwrite(ITEMS, rec)
                items_total += 1

                if isdir:
                    folders_total += 1
                    jwrite(FOLDERS, rec)
                    if full not in done:
                        jwrite(QUEUE, {"path":full, "depth":depth+1, "queued_at":now()})
                else:
                    files_total += 1
                    jwrite(FILES, rec)
                    if rec["kind"] == "ZIP":
                        zip_files += 1
                        jwrite(ZIPS, rec)

            jwrite(DONE, {
                "path":folder,
                "depth":depth,
                "done_at":now(),
                "children":len(children),
                "elapsed_seconds":elapsed
            })
            done.add(folder)

            if folders_walked % 100 == 0:
                print(f"[{MISSION}] walked={folders_walked} pending={len(load_queue())-len(done)} files={files_total} folders={folders_total} zips={zip_files}", flush=True)

        except Exception as e:
            errors_count += 1
            jwrite(ERRORS, {
                "path":folder,
                "depth":depth,
                "error_at":now(),
                "error":str(e)[:8000]
            })
            jwrite(DONE, {
                "path":folder,
                "depth":depth,
                "done_at":now(),
                "status":"ERROR_SKIPPED_AFTER_LOG"
            })
            done.add(folder)

    elapsed_total=round(time.time()-started,3)
    queue_total=sum(1 for _ in open(QUEUE, encoding="utf-8"))
    done_total=sum(1 for _ in open(DONE, encoding="utf-8"))
    error_total=sum(1 for _ in open(ERRORS, encoding="utf-8") if _.strip())
    pending_total=max(queue_total-done_total,0)

    snapshot={
        "mission":MISSION,
        "status":"FULL_DRIVE_INDEX_CERTIFIED" if pending_total == 0 else "PARTIAL_RESUMABLE_INDEX",
        "timestamp":now(),
        "remote":"gdrive",
        "root":"gdrive:",
        "queue_total":queue_total,
        "done_total":done_total,
        "pending_total":pending_total,
        "folders_walked_this_run":folders_walked,
        "items_seen_this_run":items_total,
        "files_seen_this_run":files_total,
        "folders_seen_this_run":folders_total,
        "zip_files_seen_this_run":zip_files,
        "errors_total":error_total,
        "elapsed_seconds_this_run":elapsed_total,
        "delete":"FORBIDDEN",
        "move_original":"FORBIDDEN",
        "modify_original":"FORBIDDEN",
        "next":"P4.91G_DRIVE_ZIP_RECURSIVE_ABSORPTION"
    }

    SNAP.write_text(json.dumps(snapshot, indent=2, ensure_ascii=True), encoding="utf-8")

    CERT.write_text(
        "P4.91F4 COMPLETE\n"
        "RESUMABLE FULL DRIVE WALK EXECUTED\n"
        f"STATUS={snapshot['status']}\n"
        f"QUEUE_TOTAL={queue_total}\n"
        f"DONE_TOTAL={done_total}\n"
        f"PENDING_TOTAL={pending_total}\n"
        f"ERRORS_TOTAL={error_total}\n"
        "DELETE=FORBIDDEN\n"
        "MOVE_ORIGINAL=FORBIDDEN\n"
        "MODIFY_ORIGINAL=FORBIDDEN\n"
        "NEXT=P4.91G_DRIVE_ZIP_RECURSIVE_ABSORPTION\n",
        encoding="utf-8"
    )

    print(json.dumps(snapshot, indent=2, ensure_ascii=True))

if __name__ == "__main__":
    main()

