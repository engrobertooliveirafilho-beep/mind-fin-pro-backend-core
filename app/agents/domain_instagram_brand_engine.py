"""ET665.R358 offline real domain.instagram_brand_engine component; no external I/O."""
from decimal import Decimal
from app.agents._et665_r356_common import attest,validate
AGENT_ID="domain.instagram_brand_engine"
def describe_capabilities():
    return {"agent_id":AGENT_ID,"component":"monthly_cashflow","mode":"paper_only"}
def run_dry(payload=None):
    v=validate(payload)
    net=v["revenue"]-v["fixed_costs"]-v["variable_costs"]
    output={"brand_pillar":"financial_clarity","visual_direction":{"palette":"neutral","format":"carousel_4_5"},
            "content_plan":[{"slide":1,"message":"Understand your monthly inflows"},{"slide":2,"message":"Compare fixed and variable costs"},{"slide":3,"message":"Protect cash reserves"}],
            "context":"deficit" if net<0 else "surplus","posts_published":0}
    return attest(AGENT_ID,payload,output)
