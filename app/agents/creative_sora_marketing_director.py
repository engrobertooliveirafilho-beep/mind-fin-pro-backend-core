"""ET665.R357 offline deterministic creative.sora_marketing_director real component."""
from app.agents._et665_r356_common import attest,validate
AGENT_ID="creative.sora_marketing_director"
def describe_capabilities():
    return {"agent_id":AGENT_ID,"component":"monthly_cashflow","mode":"paper_only"}
def run_dry(payload=None):
    v=validate(payload)
    net=v["revenue"]-v["fixed_costs"]-v["variable_costs"]
    output={"brief":{"objective":"cash_preservation" if net<0 else "sustainable_growth","format":"vertical_9_16","duration_seconds":15,"concept":"explain_cashflow_without_return_promises"},"variants":[{"hook":"Understand monthly cashflow","cta":"Review your budget"},{"hook":"Protect your cash reserve","cta":"Analyze your expenses"}],"generation_executed":False,"budget_authorized":"0.00"}
    return attest(AGENT_ID,payload,output)
