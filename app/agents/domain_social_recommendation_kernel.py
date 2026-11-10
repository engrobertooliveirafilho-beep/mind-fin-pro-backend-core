"""ET665.R359 deterministic offline domain.social_recommendation_kernel cashflow analysis."""
from decimal import Decimal
from app.agents._et665_r356_common import attest,validate
AGENT_ID="domain.social_recommendation_kernel"
def describe_capabilities():
    return {"agent_id":AGENT_ID,"component":"monthly_cashflow","mode":"paper_only"}
def run_dry(payload=None):
    v=validate(payload)
    net=v["revenue"]-v["fixed_costs"]-v["variable_costs"]
    candidates=[{"id":"cashflow_basics","priority":2},{"id":"expense_review","priority":3 if net<0 else 1},{"id":"reserve_planning","priority":1 if net<0 else 3}]
    ranked=sorted(candidates,key=lambda x:(-x["priority"],x["id"]))
    output={"ranked_content":ranked,"ranking_basis":"deterministic_cashflow_context",
            "personal_data_used":False,"feed_published":False}
    return attest(AGENT_ID,payload,output)
