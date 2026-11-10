"""ET665.R384: deterministic integrated E2E evidence, no fabricated certification.

Produces a local JSON artifact with SHA256 from executable 19-candidate proof,
historical Drive provenance and all 16 independent certification blockers.
"""
import argparse,hashlib,json
from pathlib import Path
from mind_trader.experimental.et665_r377_e2e_phase_b_report import run
from mind_trader.experimental.et665_r364_evidence_builder import build as original_e2e_build
from mind_trader.experimental.et665_r383_original_19_provenance import audit as provenance
from mind_trader.experimental.et665_r365_phase_b_evidence_gate import FRONTS,audit as phase_audit
from app.agents._et665_r356_common import digest

def build():
    execution=run()
    history=provenance()
    phase=phase_audit(Path("."),{"schema":"ET665.R365.v1","fronts":{}})
    if execution["candidate_e2e_status"]!="PASS" or execution["cross_agent_decision"]!="HOLD_SPEND":
        raise RuntimeError("unsafe cross-agent decision")
    if execution["candidate_executed"]!=19 or history["candidate_modules_executed"]!=19:
        raise RuntimeError("incomplete E2E execution")
    if execution["candidate_chain_sha256"]=="" or len(execution["candidate_chain_sha256"])!=64:
        raise RuntimeError("invalid chain hash")
    if phase["verified"]!=0 or phase["total"]!=16 or set(phase["fronts"])!=set(FRONTS):
        raise RuntimeError("independent phase B evidence unexpectedly changed")
    independent=original_e2e_build()
    if execution["cross_agent_decision"]!=independent["dependent_workflow"]["creative"]["recommendation"]:
        raise RuntimeError("cross-agent decision mismatch")
    if execution["candidate_chain_sha256"]!=independent["orchestration"]["chain_sha256"]:
        raise RuntimeError("orchestration chain digest mismatch")
    if execution["input_sha256"]!=independent["input"]["input_sha256"]:
        raise RuntimeError("input lineage mismatch")
    if len(execution["candidate_outputs"])!=19:
        raise RuntimeError("incomplete agent output list")
    outputs={x["agent_id"]:x["output_sha256"] for x in execution["candidate_outputs"]}
    if len(outputs)!=19 or any(outputs.get(x["agent_id"])!=x["candidate_output_sha256"] for x in history["records"]):
        raise RuntimeError("historical provenance and execution disagree")
    result={"schema":"ET665.R384.v1","status":"CANDIDATE_E2E_ATTESTED_OFFICIAL_BLOCKED",
            "component":execution["component"],"candidate_executed":19,
            "candidate_chain_sha256":execution["candidate_chain_sha256"],
            "input_sha256":execution["input_sha256"],
            "cross_agent_decision":execution["cross_agent_decision"],
            "historical_stub_sources":history["historical_sources_recovered"],
            "agent_proofs":history["records"],"phase_b_fronts":phase["fronts"],
            "phase_b_certified":0,"official_hp19_certified":0,
            "official_hp19_membership_verified":False,
            "independent_reviewer_approval":False,
            "promotion_authorized":False,"real_orders":"FORBIDDEN",
            "production_modified":False}
    result["report_sha256"]=digest(result)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    a=p.parse_args();result=build()
    path=Path(a.output)
    path.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"candidates":19,
        "official_hp19_certified":0,"phase_b_certified":0,
        "file_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}))
if __name__=="__main__":main()
