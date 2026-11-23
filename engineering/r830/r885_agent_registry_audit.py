"""R885: fail-closed static audit for MIND agent registry metadata."""
import json

FORBIDDEN_AUTORUN = {"auto_run", "auto_activate", "memory_continua"}

def audit_registry(document):
    if type(document) is str:
        try: document = json.loads(document)
        except (ValueError, TypeError): return {"status":"invalid","reason":"invalid_json","agents":0,"findings":[]}
    if type(document) is not dict or type(document.get("agents")) is not list:
        return {"status":"invalid","reason":"invalid_registry_shape","agents":0,"findings":[]}
    agents=document["agents"]
    seen=set(); findings=[]
    for i,a in enumerate(agents):
        if type(a) is not dict or type(a.get("id")) is not str or not a["id"].strip():
            findings.append({"index":i,"kind":"invalid_agent_identity"}); continue
        aid=a["id"]
        if aid in seen: findings.append({"agent":aid,"kind":"duplicate_agent_id"})
        seen.add(aid)
        steps=a.get("step_ids",[])
        if type(steps) is not list or any(type(s) is not int or s<1 for s in steps):
            findings.append({"agent":aid,"kind":"invalid_step_ids"})
        gov=a.get("governance_rules",{})
        if type(gov) is not dict:
            findings.append({"agent":aid,"kind":"invalid_governance_rules"}); gov={}
        if gov.get("can_block_actions") is True:
            findings.append({"agent":aid,"kind":"unsafe_agent_block_authority"})
        if gov.get("can_change_code") is True or gov.get("can_create_steps_directly") is True:
            findings.append({"agent":aid,"kind":"unsafe_mutation_authority"})
        health=a.get("agent_health",{})
        if type(health) is not dict or health.get("status") != "healthy":
            findings.append({"agent":aid,"kind":"health_unverified"})
        if any(a.get(flag) is True for flag in FORBIDDEN_AUTORUN):
            findings.append({"agent":aid,"kind":"autorun_flag_not_authority"})
        if a.get("active") is True and (type(health) is not dict or health.get("status") != "healthy"):
            findings.append({"agent":aid,"kind":"active_without_health_proof"})
    return {"status":"review_required" if findings else "metadata_consistent",
            "agents":len(agents),"unique_agent_ids":len(seen),"findings":findings,
            "runtime_certified":False,"dispatch_authorized":False}
