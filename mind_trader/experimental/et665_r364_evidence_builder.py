"""ET665.R364 evidence builder: 19 actual candidate results and domain dependency.

Offline, deterministic, no I/O except explicitly requested evidence file.
"""
import argparse,hashlib,json
from pathlib import Path
from mind_trader.experimental.et665_r340_safe_agent_dispatch import AGENT_MODULES,run_agent
from mind_trader.experimental.et665_r362_candidate_orchestration import run_pipeline
from mind_trader.experimental.et665_r363_dependent_workflow import run_dependent_workflow
from app.agents._et665_r356_common import digest,validate

def build():
    source={"component":"monthly_cashflow","revenue":"1000.00","fixed_costs":"2500.00",
            "variable_costs":"500.00","cash_balance":"9000.00"}
    payload={**source,"input_sha256":digest(source)}
    validate(payload)
    records=[]
    for name in AGENT_MODULES:
        result=run_agent(name,payload)
        if result.get("status")!="processed" or result.get("mode")!="paper_only" or result.get("real_orders")!="FORBIDDEN" or result.get("promotion_authorized") is not False:
            raise RuntimeError("unsafe candidate result: "+name)
        if result.get("input_sha256")!=payload["input_sha256"] or result.get("output_sha256")!=digest(result.get("output")):
            raise RuntimeError("invalid candidate lineage: "+name)
        records.append({"agent_id":result["agent_id"],"input_sha256":result["input_sha256"],
                        "output_sha256":result["output_sha256"],"output":result["output"],
                        "processed_items":result["processed_items"]})
    if len(records)!=19 or len({r["agent_id"] for r in records})!=19:
        raise RuntimeError("candidate manifest mismatch")
    pipeline=run_pipeline(payload)
    dependent=run_dependent_workflow(payload)
    if pipeline["candidate_count"]!=19 or dependent["creative"]["recommendation"]!="HOLD_SPEND":
        raise RuntimeError("cross-check failed")
    report={"schema":"ET665.R364.v1","status":"CANDIDATE_E2E_PASS",
            "input":payload,"candidate_count":len(records),"candidate_results":records,
            "orchestration":pipeline,"dependent_workflow":dependent,
            "official_hp19_certified":False,"phase_b_certified":False,
            "real_orders":"FORBIDDEN","production_modified":False}
    report["report_sha256"]=digest(report)
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    args=p.parse_args()
    report=build()
    path=Path(args.output)
    path.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False),encoding="utf-8")
    print(json.dumps({"status":report["status"],"verified":report["candidate_count"],
                      "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                      "official_hp19_certified":False,"phase_b_certified":False}))
if __name__=="__main__":main()
