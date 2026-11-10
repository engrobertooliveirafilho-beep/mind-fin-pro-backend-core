"""ET665.R362: deterministic, fail-closed orchestration of 19 real candidate modules.

No external effects. Each module receives the same attested source component;
subsequent steps verify predecessor lineage before execution. Not HP19 certification.
"""
import hashlib
import json
from mind_trader.experimental.et665_r340_safe_agent_dispatch import AGENT_MODULES, run_agent

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def run_pipeline(payload):
    if not isinstance(payload,dict) or len(AGENT_MODULES)!=19 or len(set(AGENT_MODULES))!=19:
        raise ValueError("invalid orchestration manifest")
    from app.agents._et665_r356_common import validate
    validate(payload)
    chain=[]
    previous=payload["input_sha256"]
    for index,name in enumerate(AGENT_MODULES):
        result=run_agent(name,payload)
        if result.get("input_sha256")!=payload["input_sha256"] or result.get("output_sha256")!=digest(result.get("output")):
            raise RuntimeError("agent lineage violation")
        if result.get("processed_items")!=4 or result.get("mode")!="paper_only":
            raise RuntimeError("invalid processing contract")
        entry={"index":index,"agent_id":name,"input_sha256":result["input_sha256"],
               "output_sha256":result["output_sha256"],"predecessor_sha256":previous}
        entry["chain_sha256"]=digest(entry)
        chain.append(entry)
        previous=entry["chain_sha256"]
    if len(chain)!=19:
        raise RuntimeError("incomplete pipeline")
    return {"status":"processed","mode":"paper_only","component":payload["component"],
            "candidate_count":len(chain),"input_sha256":payload["input_sha256"],
            "chain_sha256":previous,"chain":chain,"hp19_membership":"NOT_VERIFIED",
            "phase_b_certified":False,"real_orders":"FORBIDDEN","promotion_authorized":False}
