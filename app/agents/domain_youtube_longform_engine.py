"""ET665.R360 real offline domain.youtube_longform_engine analysis; no external effects."""
from app.agents._et665_r356_common import attest,validate
AGENT_ID="domain.youtube_longform_engine"
def describe_capabilities():
    return {"agent_id":AGENT_ID,"component":"monthly_cashflow","mode":"paper_only"}
def run_dry(payload=None):
    v=validate(payload)
    net=v["revenue"]-v["fixed_costs"]-v["variable_costs"]
    output={"episode_plan":{"title":"Monthly Cashflow Explained","chapters":[{"minute":0,"topic":"Revenue"},{"minute":3,"topic":"Fixed and variable costs"},{"minute":7,"topic":"Runway"}],"estimated_minutes":10},"case_net_cashflow":str(net),"uploads":0}
    return attest(AGENT_ID,payload,output)
