"""R328 Drive ZIP-inventory recovery: read-only source, fail-closed SHA audit."""
import argparse,csv,hashlib,json,os,re,subprocess,tempfile,zipfile
from pathlib import Path
from datetime import datetime,timezone
def digest(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return h.hexdigest()
def safe(name):
 name=name.replace("\\","/")
 if not name or name.startswith("/") or ":" in name or any(p in ("",".","..") for p in name.split("/")):raise ValueError("UNSAFE_PATH")
 return Path(name)
def inventory(path,member=None):
 path=Path(path)
 if path.suffix.lower()==".zip":
  with zipfile.ZipFile(path) as z:
   candidates=[n for n in z.namelist() if n.lower().endswith(".csv") and not n.endswith("/")]
   if member is None:
    if len(candidates)!=1:raise ValueError("SELECT_INVENTORY_MEMBER")
    member=candidates[0]
   safe(member)
   if member not in candidates:raise ValueError("MISSING_INVENTORY_MEMBER")
   data=z.read(member).decode("utf-8-sig").splitlines()
 else:data=path.read_text(encoding="utf-8-sig").splitlines()
 reader=csv.DictReader(data)
 if not reader.fieldnames or not ({"path","remote_path"}&set(reader.fieldnames)):raise ValueError("MISSING_PATH")
 for row in reader:
  rel=safe(row.get("remote_path") or row.get("path") or "")
  expected=(row.get("sha256") or "").strip().lower()
  if expected and not re.fullmatch("[0-9a-f]{64}",expected):raise ValueError("INVALID_SHA")
  yield rel,expected
def recover(index,remote,out,member=None,limit=0):
 if not re.fullmatch("[A-Za-z0-9_-]+:[A-Za-z0-9_./ -]*",remote) or ".." in remote:raise ValueError("UNSAFE_REMOTE")
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 ledger=out/"recovery_ledger.jsonl";counts={"verified":0,"unverified":0,"failed":0,"skipped":0};seen=set()
 for number,(rel,expected) in enumerate(inventory(index,member),1):
  if limit and number>limit:break
  key=rel.as_posix().casefold();computed=None
  if key in seen:status,reason="skipped","DUPLICATE_PATH"
  else:
   seen.add(key);target=(out/"recovered"/rel).resolve()
   if not target.is_relative_to(out/"recovered"):raise ValueError("OUTPUT_ESCAPE")
   target.parent.mkdir(parents=True,exist_ok=True)
   with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as f:tmp=Path(f.name)
   try:
    result=subprocess.run(["rclone","copyto","--",remote.rstrip("/")+"/"+rel.as_posix(),str(tmp)],capture_output=True,timeout=900)
    if result.returncode:status,reason="failed","COPY_FAILED"
    else:
     computed=digest(tmp)
     if expected and expected!=computed:status,reason="failed","SHA_MISMATCH"
     else:
      os.replace(tmp,target);status,reason=("verified","SHA_MATCH") if expected else ("unverified","NO_REFERENCE_SHA")
   except (OSError,subprocess.TimeoutExpired):status,reason="failed","TRANSPORT_ERROR"
   finally:tmp.unlink(missing_ok=True)
  counts[status]+=1
  record={"time_utc":datetime.now(timezone.utc).isoformat(),"path":rel.as_posix(),"status":status,"reason":reason,"sha256_computed":computed,"sha256_expected":expected or None}
  with ledger.open("a",encoding="utf-8") as f:f.write(json.dumps(record,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
 report={"counts":counts,"ledger_sha256":digest(ledger),"certified":counts["failed"]==counts["unverified"]==counts["skipped"]==0,"published":False}
 (out/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--inventory",required=True);p.add_argument("--member");p.add_argument("--remote",required=True);p.add_argument("--output",required=True);p.add_argument("--limit",type=int,default=0);a=p.parse_args()
 print(json.dumps(recover(a.inventory,a.remote,a.output,a.member,a.limit),indent=2))
