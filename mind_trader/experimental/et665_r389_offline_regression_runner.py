"""ET665.R389: offline regression orchestrator with atomic evidence and fail-closed exit.

Runs R384-R389 via unittest; stores exact command, output, status and SHA256.
Never alters production, triggers workflows, or authorizes real orders.
"""
import argparse,hashlib,json,os,re,subprocess,sys,tempfile
from pathlib import Path

MODULES=tuple(
    "mind_trader.tests.security_review.test_et665_r%d_%s" % (n,s)
    for n,s in (
        (384,"integrated_evidence"),
        (385,"external_evidence_inspector"),
        (386,"adversarial_chain"),
        (387,"chain_lineage_regression"),
        (388,"cross_agent_integrity"),
        (389,"offline_regression_runner"),
    )
)

def run(output_dir):
    dest=Path(output_dir).resolve()
    dest.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,"-B","-m","unittest","-v",*MODULES]
    try:
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=120,check=False,
                              env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        exit_code=result.returncode
        log=(result.stdout or "")+(result.stderr or "")
    except (subprocess.TimeoutExpired,OSError) as exc:
        exit_code=124 if isinstance(exc,subprocess.TimeoutExpired) else 127
        stdout=getattr(exc,"stdout",None) or ""
        stderr=getattr(exc,"stderr",None) or ""
        def as_text(value):
            return value.decode("utf-8","replace") if isinstance(value,bytes) else str(value)
        log=as_text(stdout)+as_text(stderr)+"\nEXECUTION_ERROR: "+type(exc).__name__+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=dest,
                                      prefix=".r389-",delete=False) as handle:
        handle.write(log)
        temp=Path(handle.name)
    path=dest/"r389_tests.log"
    temp.replace(path)
    matches=re.findall(r"(?m)^Ran (\d+) tests? in [0-9.]+s\s*$",log)
    test_count=int(matches[0]) if len(matches)==1 else 0
    passed=(exit_code==0 and len(matches)==1
            and test_count>=len(MODULES)
            and bool(re.search(r"(?m)^OK\\s*$",log))
            and "FAILED" not in log and "Traceback (most recent call last)" not in log
            and not re.search(r"(?m)^.*\\.\\.\\. skipped ",log)
            and not re.search(r"(?m)^OK \\(skipped=",log))
    evidence={"schema":"ET665.R389.v1","status":"PASS" if passed else "FAIL_CLOSED",
              "exit_code":exit_code,"command":cmd[1:],"test_count":test_count,
              "log_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
              "test_modules":list(MODULES),
              "official_hp19_certified":0,"phase_b_certified":0,
              "real_orders":"FORBIDDEN","production_modified":False}
    report=dest/"r389_evidence.json"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=dest,
                                      prefix=".r389-json-",delete=False) as handle:
        json.dump(evidence,handle,indent=2,sort_keys=True)
        handle.write("\n")
        temp=Path(handle.name)
    temp.replace(report)
    return evidence

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    args=parser.parse_args()
    r=run(args.output_dir)
    print(json.dumps(r,sort_keys=True))
    return 0 if r["status"]=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())
