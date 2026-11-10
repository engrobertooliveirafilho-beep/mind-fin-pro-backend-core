"""ET665.R360 real offline domain.tiktok_growth_engine analysis; no external effects."""
from app.agents._et665_r356_common import attest,validate
AGENT_ID="domain.tiktok_growth_engine"
def describe_capabilities():
    return {"agent_id":AGENT_ID,"component":"monthly_cashflow","mode":"paper_only"}
def run_dry(payload=None):
    v=validate(payload)
    deficit=v["revenue"]<v["fixed_costs"]+v["variable_costs"]
    output={"short_video_plan":{"length_seconds":20,"hook":"What is your cash runway?","segments":[{"second":0,"topic":"income"},{"second":7,"topic":"costs"},{"second":14,"topic":"cash_reserve"}]},"priority":"education_not_paid_growth" if deficit else "organic_experiment","videos_published":0}
    return attest(AGENT_ID,payload,output)
