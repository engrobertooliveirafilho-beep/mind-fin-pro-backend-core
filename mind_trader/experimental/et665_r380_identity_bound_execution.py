"""ET665.R380: explicit identity-bound candidate execution and output proof.

Never imports the historical collision-prone dispatcher. PAPER-only.
"""
from importlib import import_module
from mind_trader.experimental.et665_r340_safe_agent_dispatch import AGENT_MODULES,run_agent
from mind_trader.experimental.et665_r364_evidence_builder import build

def verify():
    report=build()
    records=report["candidate_results"]
    if len(records)!=len(AGENT_MODULES) or len(records)!=19:
        raise RuntimeError("incomplete candidate execution")
    proof=[]
    for name,record in zip(AGENT_MODULES,records):
        module=import_module("app.agents."+name)
        expected=name.replace("_",".",1)
        if module.__name__!="app.agents."+name or getattr(module,"AGENT_ID",None)!=expected:
            raise RuntimeError("wrong executor module: "+name)
        if record["agent_id"]!=expected:
            raise RuntimeError("wrong output identity: "+name)
        capabilities=module.describe_capabilities()
        if not isinstance(capabilities,dict) or capabilities.get("agent_id")!=expected:
            raise RuntimeError("capability identity mismatch: "+name)
        if not callable(getattr(module,"run_dry",None)):
            raise RuntimeError("missing original-style run_dry contract: "+name)
        result=run_agent(name,report["input"])
        if result["output_sha256"]!=record["output_sha256"] or result["output"]!=record["output"]:
            raise RuntimeError("nondeterministic or swapped execution: "+name)
        proof.append({"agent_id":expected,"module":module.__name__,"output_sha256":result["output_sha256"]})
    if len({p["module"] for p in proof})!=19 or len({p["agent_id"] for p in proof})!=19:
        raise RuntimeError("duplicate executor identity")
    return {"status":"CANDIDATE_IDENTITY_BOUND_E2E_PASS","candidate_executed":19,
            "proof":proof,"input_sha256":report["input"]["input_sha256"],
            "historical_original_executors_verified":False,
            "official_hp19_certified":0,"phase_b_certified":0,
            "real_orders":"FORBIDDEN","production_modified":False}
