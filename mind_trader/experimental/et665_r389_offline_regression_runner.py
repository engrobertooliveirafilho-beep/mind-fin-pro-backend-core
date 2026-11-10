"""ET665.R389: offline regression orchestrator with atomic evidence and fail-closed exit.

Runs R384-R388 via unittest; stores exact command, output, status and SHA256.
Never alters production, triggers workflows, or authorizes real orders.
"""
import argparse,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path

MODULES=tuple(
    "mind_trader.tests.security_review.test_et665_r%d_%s" % (n,s)
    for n,s in (
        (384,"integrated_evidence"),
        (385,"external_evidence_inspector"),
        (386,"adversarial_chain"),
        (387,"chain_lineage_regression"),
        (388,"cross_agent_integrity"),
    )
)

def run(output_dir):
    dest=Path(output_dir).resolve()
    dest.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,"-B","-m","unittest","-v",*MODULES]
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=120,check=False,
                          env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
    log=(result.stdout or "")+(result.stderr or "")
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=dest,
                                      prefix=".r389-",delete=False) as handle:
        handle.write(log)
        temp=Path(handle.name)
    path=dest/"r389_tests.log"
    temp.replace(path)
    passed=result.returncode==0 and "OK" in log and "FAILED" not in log
    evidence={"schema":"ET665.R389.v1","status":"PASS" if passed else "FAIL_CLOSED",
              "exit_code":result.returncode,"command":cmd[1:],
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
