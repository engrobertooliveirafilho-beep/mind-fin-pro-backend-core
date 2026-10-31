"""R330: enumerate real files under R4 directory prefixes, no source mutation.

Requires authenticated local rclone. Emits manifest and checkpoint; no auto-promotion.
"""
import argparse,csv,hashlib,json,subprocess
from pathlib import Path
def enumerate_files(prefixes,output,remote="gdrive:MIND",batch=100,offset=0):
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 with open(prefixes,newline="",encoding="utf-8-sig") as f:
  reader=csv.DictReader(f)
  if reader.fieldnames!=["Remote","Count","Recovered"]:raise ValueError("R4_SCHEMA_MISMATCH")
  rows=list(reader)
 selected=rows[offset:offset+batch]
 if any(not r["Remote"].startswith("GDRIVE:") or not r["Remote"].endswith("/") or ".." in r["Remote"] for r in selected):raise ValueError("UNSAFE_PREFIX")
 manifest=output/"files.jsonl";ledger=output/"batches.jsonl";files=0;errors=0
 with manifest.open("a",encoding="utf-8") as out,ledger.open("a",encoding="utf-8") as log:
  for i,row in enumerate(selected,offset):
   prefix=row["Remote"][len("GDRIVE:"):].lstrip("/")
   cmd=["rclone","lsjson","--recursive","--files-only","--hash","--",remote.rstrip("/")+"/"+prefix]
   try:
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=900)
    if p.returncode:raise RuntimeError("RCLONE_ENUMERATION_FAILED")
    items=json.loads(p.stdout)
    for item in items:
     rel=item["Path"]
     if rel.startswith("/") or ".." in Path(rel).parts:raise ValueError("UNSAFE_FILE_PATH")
     record={"prefix":prefix,"path":prefix+rel,"size":item.get("Size"),"modtime":item.get("ModTime"),"remote_hashes":item.get("Hashes",{}),"sha256_local":None,"verification":"NOT_RECOVERED"}
     out.write(json.dumps(record,sort_keys=True)+"\n");files+=1
    status="ENUMERATED"
   except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired):status="FAILED";errors+=1
   log.write(json.dumps({"index":i,"prefix":prefix,"status":status},sort_keys=True)+"\n");out.flush();log.flush()
 report={"prefixes_attempted":len(selected),"files_listed":files,"failed_prefixes":errors,"recovered_bytes":0,"sha256_verified_files":0,"mass_recovery_certified":False}
 (output/"enumeration_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--prefixes",required=True);p.add_argument("--output",required=True);p.add_argument("--remote",default="gdrive:MIND");p.add_argument("--batch",type=int,default=100);p.add_argument("--offset",type=int,default=0)
 a=p.parse_args();print(json.dumps(enumerate_files(a.prefixes,a.output,a.remote,a.batch,a.offset),indent=2))
