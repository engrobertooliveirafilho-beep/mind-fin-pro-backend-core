"""ET665.R385: verify supplied Phase B evidence without manufacturing approvals.

This is an inspection-only report. Even 16 valid manifest records are NOT
an independent security audit, HP19 authority proof, or permission to promote.
"""
import argparse,json,hashlib
from pathlib import Path
from mind_trader.experimental.et665_r384_integrated_evidence import build
from mind_trader.experimental.et665_r365_phase_b_evidence_gate import audit,FRONTS
from app.agents._et665_r356_common import digest

def inspect(evidence_root,manifest):
    baseline=build()
    reviewed=audit(Path(evidence_root),manifest)
    if reviewed["total"]!=16 or set(reviewed["fronts"])!=set(FRONTS):
        raise RuntimeError("front inventory mismatch")
    if baseline["candidate_executed"]!=19 or baseline["real_orders"]!="FORBIDDEN":
        raise RuntimeError("candidate baseline invalid")
    result={"schema":"ET665.R385.v1","status":"REVIEW_REQUIRED",
        "candidate_executed":19,"historical_stub_sources":19,
        "evidence_records_passing_schema_hash_and_flag":reviewed["verified"],
        "evidence_fronts":reviewed["fronts"],
        "external_review_independently_authenticated":False,
        "official_hp19_membership_verified":False,"official_hp19_certified":0,
        "phase_b_independently_certified":0,
        "candidate_chain_sha256":baseline["candidate_chain_sha256"],
        "real_orders":"FORBIDDEN","promotion_authorized":False,
        "production_modified":False}
    result["report_sha256"]=digest(result)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--evidence-root",required=True)
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--output",required=True)
    a=parser.parse_args()
    manifest=json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    result=inspect(a.evidence_root,manifest)
    out=Path(a.output)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"records":result["evidence_records_passing_schema_hash_and_flag"],"phase_b_independently_certified":0,"sha256":hashlib.sha256(out.read_bytes()).hexdigest()}))
if __name__=="__main__":main()
