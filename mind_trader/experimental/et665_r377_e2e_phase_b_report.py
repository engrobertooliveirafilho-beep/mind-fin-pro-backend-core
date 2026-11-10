"""ET665.R377: reproducible E2E candidate execution + Phase B coverage.

Executes the real monthly_cashflow computation through 19 candidate modules.
Explicitly distinguishes 19 candidate computations from official HP19 contracts.
"""
import argparse,json,hashlib
from pathlib import Path
from mind_trader.experimental.et665_r364_evidence_builder import build
from mind_trader.experimental.et665_r365_phase_b_evidence_gate import FRONTS
from app.agents._et665_r356_common import digest

def run():
    report=build()
    records=report["candidate_results"]
    if len(records)!=19 or len({r["agent_id"] for r in records})!=19:
        raise RuntimeError("19 candidate executions required")
    if any(not isinstance(r["output"],dict) or r["processed_items"]!=4 for r in records):
        raise RuntimeError("incomplete component processing")
    if report["dependent_workflow"]["creative"]["recommendation"]!="HOLD_SPEND":
        raise RuntimeError("cross-agent decision not enforced")
    result={"schema":"ET665.R377.v1","component":"monthly_cashflow",
            "candidate_e2e_status":"PASS","candidate_executed":19,
            "candidate_chain_sha256":report["orchestration"]["chain_sha256"],
            "input_sha256":report["input"]["input_sha256"],
            "candidate_outputs":[{"agent_id":r["agent_id"],"output_sha256":r["output_sha256"]} for r in records],
            "cross_agent_decision":"HOLD_SPEND",
            "official_hp19_verified":0,"official_hp19_total":19,
            "phase_b_certified":0,"phase_b_total":len(FRONTS),
            "phase_b_missing_evidence":list(FRONTS),
            "production_modified":False,"strategy_promotion_authorized":False,
            "real_orders":"FORBIDDEN"}
    result["sha256"]=digest(result)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    a=p.parse_args();report=run();out=Path(a.output)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["candidate_e2e_status"],"candidates":19,
                      "official_hp19_verified":0,"phase_b_certified":0,
                      "file_sha256":hashlib.sha256(out.read_bytes()).hexdigest()}))
if __name__=="__main__":main()
