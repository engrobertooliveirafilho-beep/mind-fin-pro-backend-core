"""ET665.R359 deterministic offline domain.napoleon_hill_engine cashflow analysis."""
from decimal import Decimal
from app.agents._et665_r356_common import attest,validate
AGENT_ID="domain.napoleon_hill_engine"
def describe_capabilities():
    return {"agent_id":AGENT_ID,"component":"monthly_cashflow","mode":"paper_only"}
def run_dry(payload=None):
    v=validate(payload)
    net=v["revenue"]-v["fixed_costs"]-v["variable_costs"]
    output={"framework":"goal_action_review","goal":"nonnegative_monthly_cashflow",
            "gap_to_goal":str(max(-net,Decimal("0"))),"actions":[{"priority":1,"action":"audit_fixed_costs","amount":str(v["fixed_costs"])},{"priority":2,"action":"audit_variable_costs","amount":str(v["variable_costs"])}],
            "evidence_basis":"provided_cashflow_only","historical_quote_claimed":False}
    return attest(AGENT_ID,payload,output)
