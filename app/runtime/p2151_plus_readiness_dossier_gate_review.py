from __future__ import annotations
import json, os, hashlib, time
from pathlib import Path

LOCKS = {
    "MIND_MODE":"PAPER_ONLY",
    "REAL_ORDERS":"FORBIDDEN",
    "LIVE_TRADING":"FALSE",
    "BROKER_EXECUTION":"DISABLED",
    "FINANCIAL_EXECUTION":"DISABLED",
    "FTMO_REAL":"FORBIDDEN",
    "SEND_ORDER":"BLOCKED",
    "MT5_ORDER_SEND":"BLOCKED",
    "BROKER_API_CALL":"BLOCKED",
}

def enforce():
    for k,v in LOCKS.items():
        os.environ[k]=v
    return dict(LOCKS)

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def load(path):
    import math
    p=Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    def unique_keys(pairs):
        result={}
        for key,value in pairs:
            if key in result:
                raise ValueError("P2151_DUPLICATE_JSON_KEY")
            result[key]=value
        return result

    def finite_float(value):
        parsed=float(value)
        if not math.isfinite(parsed):
            raise ValueError("P2151_NONFINITE_JSON_NUMBER")
        return parsed

    def reject_constant(value):
        raise ValueError("P2151_NONFINITE_JSON_NUMBER")

    data=json.loads(
        p.read_text(encoding="utf-8"),
        object_pairs_hook=unique_keys,
        parse_float=finite_float,
        parse_constant=reject_constant,
    )
    if not isinstance(data,dict):
        raise ValueError("P2151_INVALID_CERTIFICATION_OBJECT")
    return data

def run_p2151_plus(output_dir="data/runtime/P2151_PLUS/evidence"):
    # Fail closed on unsafe caller settings; never overwrite evidence of drift.
    for k,v in LOCKS.items():
        observed=os.environ.get(k)
        if observed is not None and observed!=v:
            raise RuntimeError(f"{k}_LOCK_BREACH")
    enforce()
    out=Path(output_dir)

    deps = {
        "P2071_2080": "data/runtime/P2071_2080/evidence/P2071_2080_FINAL_CERTIFICATION.json",
        "P2081_2090": "data/runtime/P2081_2090/evidence/P2081_2090_FINAL_CERTIFICATION.json",
        "P2091_2100": "data/runtime/P2091_2100/evidence/P2091_2100_FINAL_CERTIFICATION.json",
        "P2101_2110": "data/runtime/P2101_2110/evidence/P2101_2110_FINAL_CERTIFICATION.json",
        "P2111_2120": "data/runtime/P2111_2120/evidence/P2111_2120_FINAL_CERTIFICATION.json",
        "P2121_PLUS": "data/runtime/P2121_PLUS/evidence/P2121_PLUS_FINAL_CERTIFICATION.json",
        "P2131_2150": "data/runtime/P2131_2150/evidence/P2131_2150_FINAL_CERTIFICATION.json",
    }

    blocks={}
    missing=[]
    failed=[]
    hashes={}

    for k,p in deps.items():
        if not Path(p).exists():
            missing.append(p)
            continue
        data=load(p)
        blocks[k]={"status":data.get("status"),"readiness":data.get("readiness"),"path":p}
        hashes[k]=sha(p)
        expected={
            "P2071_2080":"REALTIME_PAPER_RUNTIME_CERTIFIED",
            "P2081_2090":"REALTIME_PORTFOLIO_GOVERNANCE_CERTIFIED",
            "P2091_2100":"REALTIME_INTELLIGENCE_LAYER_CERTIFIED",
            "P2101_2110":"AUTONOMOUS_PAPER_OPERATIONS_CERTIFIED",
            "P2111_2120":"MAXIMUM_TECHNICAL_CAPACITY_CERTIFIED",
            "P2121_PLUS":"CONTINUOUS_MAX_CAPACITY_CERTIFIED",
            "P2131_2150":"FTMO_PAPER_COMPLIANCE_AND_OPERATIONAL_ASSURANCE_CERTIFIED",
        }[k]
        if data.get("status")!="PASS" or data.get("readiness")!=expected:
            failed.append(k)

    gate_review = {
        "allowed_environment": [
            "LOCAL_PAPER_RUNTIME",
            "INTERNAL_SIMULATION",
            "AUDIT_REPLAY",
            "FTMO_SIMULATOR_REVIEW_WITHOUT_BROKER_EXECUTION"
        ],
        "forbidden_environment": [
            "REAL_ACCOUNT",
            "LIVE_TRADING",
            "BROKER_EXECUTION",
            "MT5_ORDER_SEND",
            "FINANCIAL_ROUTING",
            "FTMO_REAL"
        ],
        "deployment_decision": "BLOCKED",
        "real_execution_decision": "FORBIDDEN",
        "broker_connection_decision": "FORBIDDEN",
        "financial_execution_decision": "FORBIDDEN"
    }

    mission_status = {
        "P2151_READINESS_DOSSIER_BUILD": "PASS" if not missing else "FAIL",
        "P2152_DEPENDENCY_CHAIN_REVIEW": "PASS" if not missing and not failed else "FAIL",
        "P2153_GATE_POLICY_REVIEW": "PASS",
        "P2154_ALLOWED_ENVIRONMENT_DECLARATION": "PASS",
        "P2155_FORBIDDEN_ENVIRONMENT_DECLARATION": "PASS",
        "P2156_FINANCIAL_LOCK_RECONFIRMATION": "PASS" if enforce()==LOCKS else "FAIL",
        "P2157_EVIDENCE_HASH_REGISTRY": "PASS" if len(hashes)==len(deps) else "FAIL",
        "P2158_EXECUTIVE_SUMMARY_GENERATION": "PASS",
        "P2159_DEPLOYMENT_GATE_DECISION": "PASS" if gate_review["deployment_decision"]!="BLOCKED" else "FAIL",
        "P2160_READINESS_DOSSIER_CERTIFICATION": "PENDING",
    }

    mission_status["P2160_READINESS_DOSSIER_CERTIFICATION"] = (
        "PASS" if all(v=="PASS" for v in mission_status.values() if v!="PENDING") else "FAIL"
    )

    all_pass=all(v=="PASS" for v in mission_status.values())

    result = {
        "program":"P2151_PLUS_READINESS_DOSSIER_AND_DEPLOYMENT_GATE_REVIEW",
        "status":"PASS" if all_pass else "FAIL",
        "readiness":"PAPER_ONLY_SIMULATION_REVIEW_READY" if all_pass else "NOT_READY",
        "absolute_restrictions":enforce(),
        "certified_blocks":blocks,
        "missing":missing,
        "failed":failed,
        "hashes":hashes,
        "mission_status":mission_status,
        "gate_review":gate_review,
        "executive_conclusion":{
            "technical_capacity":"NOT_CERTIFIED",
            "continuous_audit":"NOT_CERTIFIED",
            "ftmo_paper_compliance":"NOT_CERTIFIED",
            "operational_assurance":"NOT_CERTIFIED",
            "paper_only_simulation_review":"READY" if all_pass else "NOT_READY",
            "real_orders":"FORBIDDEN",
            "broker_execution":"DISABLED",
            "financial_execution":"DISABLED",
            "live_trading":False
        },
        "next_block":"P2161_PLUS_DRY_RUN_OBSERVABILITY_AND_HUMAN_REVIEW_GATE"
    }

    out.mkdir(parents=True,exist_ok=True)
    (out/"P2151_PLUS_FINAL_CERTIFICATION.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P2151_PLUS_GATE_REVIEW.json").write_text(json.dumps(gate_review,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P2151_PLUS_DOSSIER_STATE.json").write_text(json.dumps(result["executive_conclusion"],indent=2,ensure_ascii=False),encoding="utf-8")

    md = f"""# MIND TRADER — P2151+ READINESS DOSSIER

## STATUS
{result["status"]}

## READINESS
{result["readiness"]}

## CERTIFIED BLOCKS
{json.dumps(blocks, indent=2, ensure_ascii=False)}

## GATE REVIEW
{json.dumps(gate_review, indent=2, ensure_ascii=False)}

## EXECUTIVE CONCLUSION
{json.dumps(result["executive_conclusion"], indent=2, ensure_ascii=False)}

## ABSOLUTE RESTRICTIONS
{json.dumps(result["absolute_restrictions"], indent=2, ensure_ascii=False)}

## FINAL DECISION
PAPER_ONLY simulation review blocked pending independently verified behavioral certification.
Real orders remain forbidden.
Broker execution remains disabled.
Financial execution remains disabled.
"""
    (out/"P2151_PLUS_READINESS_DOSSIER.md").write_text(md,encoding="utf-8")
    return result

if __name__=="__main__":
    print(json.dumps(run_p2151_plus(),indent=2,ensure_ascii=False))
