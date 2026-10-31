"""R334: read-only, resumable Drive ID recovery. Never promotes code."""
import argparse, hashlib, json, os, re, subprocess, tempfile
from pathlib import Path
ID=re.compile(r"^[A-Za-z0-9_-]{15,128}$")
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def recover(queue,output,remote="gdrive:",limit=0):
 if not re.fullmatch(r"[A-Za-z0-9_-]+:",remote):raise ValueError("UNSAFE_REMOTE")
 items=[json.loads(s) for s in Path(queue).read_text(encoding="utf-8").splitlines() if s.strip()]
 if not items:raise ValueError("EMPTY_QUEUE")
 ids=set()
 for r in items:
  if not ID.fullmatch(r.get("id","")) or r["id"] in ids:raise ValueError("INVALID_OR_DUPLICATE_ID")
  ids.add(r["id"])
  if not isinstance(r.get("size"),int) or r["size"]<0:raise ValueError("INVALID_SIZE")
  if r.get("sha256_expected") and not re.fullmatch(r"[a-fA-F0-9]{64}",r["sha256_expected"]):raise ValueError("INVALID_HASH")
 root=Path(output);store=root/"objects";store.mkdir(parents=True,exist_ok=True)
 done=failed=0
 with (root/"recovery.jsonl").open("a",encoding="utf-8") as log:
  for r in sorted(items,key=lambda x:(x.get("priority",99),x["id"]))[:limit or None]:
   target=store/r["id"]; expected=r.get("sha256_expected"); status="FAILED"; actual=None
   if target.is_file() and target.stat().st_size==r["size"]:
    actual=sha(target)
    if not expected or actual.lower()==expected.lower():status="HASH_MATCH" if expected else "STAGED_UNVERIFIED"
   if status=="FAILED":
    for attempt in range(3):
     fd,tmp=tempfile.mkstemp(dir=store,prefix=".partial-");os.close(fd)
     try:
      proc=subprocess.run(["rclone","backend","copyid",remote,r["id"],tmp],capture_output=True,timeout=600)
      if proc.returncode==0 and Path(tmp).stat().st_size==r["size"]:
       actual=sha(tmp)
       if not expected or actual.lower()==expected.lower():
        os.replace(tmp,target);status="HASH_MATCH" if expected else "STAGED_UNVERIFIED";break
     except (OSError,subprocess.TimeoutExpired):pass
     finally:Path(tmp).unlink(missing_ok=True)
   done+=status!="FAILED";failed+=status=="FAILED"
   log.write(json.dumps({"id":r["id"],"status":status,"sha256":actual,"expected":expected,"authority":False,"publication_approved":False})+"\n");log.flush()
 report={"queue_total":len(items),"attempted":done+failed,"staged":done,"failed":failed,"fully_recovered":False,"authority_verified":False,"github_publication_approved":False}
 (root/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--queue",required=True);p.add_argument("--output",required=True);p.add_argument("--remote",default="gdrive:");p.add_argument("--limit",type=int,default=0)
 a=p.parse_args();print(json.dumps(recover(a.queue,a.output,a.remote,a.limit),indent=2))
