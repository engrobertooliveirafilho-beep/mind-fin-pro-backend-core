"""ET665.R400: offline Docker gate for actual component processing.
Requires an independently supplied manifest; no candidate is certified automatically.
Each component is run in a separate no-network, read-only, unprivileged container.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(root, manifest, output):
    root = Path(root).resolve()
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {"status":"FAIL_CLOSED", "official_hp19_certified":0,
              "phase_b_certified":0, "runs":[]}
    try:
        data=json.loads(Path(manifest).read_text(encoding="utf-8"))
        components=data["components"]
        if not isinstance(components,list) or not components:
            raise ValueError("empty component inventory")
        seen=set()
        for index,item in enumerate(components):
            name=item["historical_id"]
            relative=item["component"]
            expected=item["sha256"]
            if not isinstance(name,str) or not name or name in seen:
                raise ValueError("duplicate/missing historical id")
            seen.add(name)
            component=(root/relative).resolve()
            if not component.is_relative_to(root) or not component.is_file() or component.is_symlink():
                raise ValueError("unsafe component")
            if sha(component)!=expected:
                raise ValueError("source hash mismatch")
            input_file=(root/item["input"]).resolve()
            if not input_file.is_relative_to(root) or not input_file.is_file() or input_file.is_symlink():
                raise ValueError("unsafe input")
            if sha(input_file)!=item["input_sha256"]:
                raise ValueError("input hash mismatch")
            # No host network, no host writes, no Docker socket, no broker secrets.
            command=["docker","run","--rm","--network","none","--read-only",
                     "--cap-drop","ALL","--security-opt","no-new-privileges",
                     "--pids-limit","64","--memory","256m","--cpus","1",
                     "--user","65534:65534",
                     "--mount",f"type=bind,src={root},dst=/work,readonly",
                     "--workdir","/work","python:3.11-alpine",
                     "python","-B",relative]
            try:
                result=subprocess.run(command,input=input_file.read_bytes(),capture_output=True,timeout=60)
                entry={"historical_id":name,"exit_code":result.returncode,
                       "source_sha256":sha(component),"input_sha256":sha(input_file),
                       "stdout_sha256":hashlib.sha256(result.stdout).hexdigest(),
                       "stderr_sha256":hashlib.sha256(result.stderr).hexdigest(),
                       "status":"EXECUTED_UNCERTIFIED" if result.returncode==0 and result.stdout else "FAIL_CLOSED"}
                # Preserve actual bytes; a hash alone does not prove behavior.
                (output/f"run_{index:02d}.stdout").write_bytes(result.stdout)
                (output/f"run_{index:02d}.stderr").write_bytes(result.stderr)
            except (OSError,subprocess.TimeoutExpired) as exc:
                entry={"historical_id":name,"status":"FAIL_CLOSED","error":type(exc).__name__}
            report["runs"].append(entry)
        if len(report["runs"])==len(components) and all(x["status"]=="EXECUTED_UNCERTIFIED" for x in report["runs"]):
            report["status"]="EXECUTED_UNCERTIFIED"
    except (OSError,ValueError,KeyError,TypeError) as exc:
        report["error"]=type(exc).__name__ + ": " + str(exc)
    (output/"r400_report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=run(args.root,args.manifest,args.output)
    print(json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="EXECUTED_UNCERTIFIED" else 1

if __name__=="__main__":
    raise SystemExit(main())
