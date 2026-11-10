"""ET665.R365 Phase B evidence gate: 16 independent fronts, fail-closed.

Does not certify based on candidate E2E or tests alone. Each front requires
a separate independently auditable evidence record. No automatic promotion.
"""
import argparse,hashlib,json
from pathlib import Path

FRONTS=(
 "mt5_access_isolation","subprocess_isolation","paper_gateway_adversarial",
 "docker_offline_reproducibility","strategy_promotion_guard",
 "risk_limits_and_kill_switch","chronological_data_provenance",
 "train_validation_test_anti_leakage","spread_slippage_commission_model",
 "strategy_individual_backtests","portfolio_combined_backtests",
 "historical_p2405_integration","hp19_authoritative_membership",
 "hp19_domain_e2e","cross_agent_failure_propagation",
 "source_authority_and_ledger_reconciliation")
REQUIRED=("front_id","status","artifact_sha256","artifact_path","test_command",
          "exit_code","commit_sha","reviewer_approval")

def verify_record(front,record,root):
    if not isinstance(record,dict) or set(record)!=set(REQUIRED):
        return "invalid evidence schema"
    if record["front_id"]!=front or record["status"]!="PASS" or record["exit_code"]!=0 or record["reviewer_approval"] is not True:
        return "missing independent PASS and human review"
    h=record["artifact_sha256"]
    if not isinstance(h,str) or len(h)!=64 or any(c not in "0123456789abcdef" for c in h.lower()):
        return "invalid sha256"
    if not isinstance(record["test_command"],str) or not record["test_command"].strip():
        return "missing test command"
    if not isinstance(record["commit_sha"],str) or len(record["commit_sha"])<7:
        return "missing commit identity"
    path=record["artifact_path"]
    if not isinstance(path,str):
        return "invalid artifact path"
    base=root.resolve()
    target=(base/path).resolve()
    if not target.is_relative_to(base) or not target.is_file() or target.is_symlink():
        return "artifact unavailable or unsafe path"
    if hashlib.sha256(target.read_bytes()).hexdigest()!=h.lower():
        return "artifact hash mismatch"
    return None

def audit(root,manifest):
    if not isinstance(manifest,dict) or set(manifest)!={"schema","fronts"} or manifest["schema"]!="ET665.R365.v1" or not isinstance(manifest["fronts"],dict):
        raise ValueError("invalid manifest")
    if set(manifest["fronts"])-set(FRONTS):
        raise ValueError("unknown front")
    results={}
    for front in FRONTS:
        record=manifest["fronts"].get(front)
        results[front]="MISSING" if record is None else ("PASS" if verify_record(front,record,root) is None else "BLOCKED")
    passed=sum(x=="PASS" for x in results.values())
    return {"status":"PASS" if passed==16 else "FAIL_CLOSED","verified":passed,"total":16,
            "fronts":results,"promotion_authorized":False,"real_orders":"FORBIDDEN"}

def main():
    p=argparse.ArgumentParser();p.add_argument("--evidence-root",required=True)
    p.add_argument("--manifest",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    root=Path(a.evidence_root)
    manifest=json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    result=audit(root,manifest)
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"status":result["status"],"verified":result["verified"],"total":16}))
    return 0 if result["status"]=="PASS" else 1
if __name__=="__main__":
    raise SystemExit(main())
