"""ET665.R363: verified cross-agent decision dependency, no external I/O.

A finance output determines the risk gate; that gate determines whether a
creative plan may be proposed. This is a *three-agent* domain workflow, not
proof of cross-dependencies across all 19 candidate modules.
"""
from app.agents._et665_r356_common import digest,validate
from mind_trader.experimental.et665_r340_safe_agent_dispatch import run_agent

def run_dependent_workflow(payload):
    validate(payload)
    finance=run_agent("domain_economics_finance_markets",payload)
    safety=run_agent("core_safety_compliance_hub",payload)
    creative=run_agent("creative_sora_marketing_director",payload)
    for item in (finance,safety,creative):
        if item.get("status")!="processed" or item.get("mode")!="paper_only":
            raise RuntimeError("agent execution failed")
        if item.get("input_sha256")!=payload["input_sha256"] or item.get("output_sha256")!=digest(item.get("output")):
            raise RuntimeError("agent lineage violation")
        if item.get("real_orders")!="FORBIDDEN" or item.get("promotion_authorized") is not False:
            raise RuntimeError("unsafe agent response")
    margin=finance["output"]["operating_margin_pct"]
    risk_flags=safety["output"].get("risk_flags")
    if margin is None or not isinstance(risk_flags,list):
        raise RuntimeError("unverifiable financial or risk output")
    from decimal import Decimal,InvalidOperation
    try:
        margin_value=Decimal(margin)
    except (InvalidOperation,TypeError):
        raise RuntimeError("invalid finance margin")
    if not margin_value.is_finite():
        raise RuntimeError("nonfinite finance margin")
    risk_block=margin_value<0 or bool(risk_flags)
    objective=creative["output"].get("brief",{}).get("objective")
    if objective not in ("cash_preservation","sustainable_growth"):
        raise RuntimeError("invalid creative objective")
    if risk_block and objective!="cash_preservation":
        raise RuntimeError("creative recommendation violates finance risk gate")
    finance_attestation=digest({"agent_id":finance["agent_id"],"output_sha256":finance["output_sha256"]})
    risk_decision={"finance_attestation":finance_attestation,"safety_output_sha256":safety["output_sha256"],
                   "margin_pct":margin,"risk_flags":risk_flags,"blocked":risk_block}
    risk_sha=digest(risk_decision)
    final={"risk_decision_sha256":risk_sha,"creative_output_sha256":creative["output_sha256"],
           "creative_objective":objective,"recommendation":"HOLD_SPEND" if risk_block else "REVIEW_ONLY",
           "campaigns_executed":0,"human_approval_required":True}
    return {"status":"processed","mode":"paper_only","finance":finance_attestation,
            "risk":risk_decision,"risk_sha256":risk_sha,"creative":final,
            "final_sha256":digest(final),"real_orders":"FORBIDDEN",
            "promotion_authorized":False,"hp19_certified":False,"phase_b_certified":False}
