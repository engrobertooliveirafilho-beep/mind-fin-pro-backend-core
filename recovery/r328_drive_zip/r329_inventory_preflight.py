"""R329 preflight for R324 directory-only inventory; blocks unsafe mass recovery."""
import csv,hashlib,json,sys
from pathlib import Path
REFERENCE_SHA="8EA67DFDFB6AEAB6128DAEB84AD27A03861FC39B6634A8D4723C6D98052E340F"
def preflight(path):
 p=Path(path)
 actual=hashlib.sha256(p.read_bytes()).hexdigest().upper()
 if actual!=REFERENCE_SHA:raise ValueError("INVENTORY_SHA_MISMATCH")
 with p.open(newline="",encoding="utf-8-sig") as handle:
  reader=csv.DictReader(handle)
  if reader.fieldnames!=["Remote","Count","Recovered"]:raise ValueError("UNEXPECTED_SCHEMA")
  total=directories=files=recovered=0;seen=set()
  for row in reader:
   remote=row["Remote"]
   if not remote.startswith("GDRIVE:") or ".." in remote:raise ValueError("UNSAFE_REMOTE")
   if remote in seen:raise ValueError("DUPLICATE_REMOTE")
   seen.add(remote);total+=1
   directories+=remote.endswith("/")
   files+=not remote.endswith("/")
   recovered+=row["Recovered"]=="1"
 return {"source_sha256":actual,"entries":total,"directory_prefixes":directories,
         "file_entries":files,"historically_recovered":recovered,
         "per_file_sha_available":False,"mass_file_recovery_authorized":False,
         "status":"BLOCKED_DIRECTORY_ONLY_INDEX"}
if __name__=="__main__":
 result=preflight(sys.argv[1]);print(json.dumps(result,indent=2))
 sys.exit(2 if result["file_entries"]==0 else 0)
