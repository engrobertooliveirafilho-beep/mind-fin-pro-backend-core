"""ET665.R359 deterministic offline domain.psychology_mindset cashflow analysis."""
from decimal import Decimal
from app.agents._et665_r356_common import attest,validate
AGENT_ID="domain.psychology_mindset"
def describe_capabilities():
    return {"agent_id":AGENT_ID,"component":"monthly_cashflow","mode":"paper_only"}
def run_dry(payload=None):
    v=validate(payload)
    net=v["revenue"]-v["fixed_costs"]-v["variable_costs"]
    output={"behavioral_prompt":"review_spending_weekly" if net<0 else "maintain_tracking",
            "habit_plan":{"frequency":"weekly","task":"compare_actual_expenses_with_budget"},
            "financial_stress_indicator":"cashflow_deficit" if net<0 else "no_cashflow_deficit",
            "mental_health_diagnosis":None,"medical_advice":False}
    return attest(AGENT_ID,payload,output)
