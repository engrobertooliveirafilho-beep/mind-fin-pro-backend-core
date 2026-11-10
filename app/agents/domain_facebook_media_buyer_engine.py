"""ET665.R358 offline real domain.facebook_media_buyer_engine component; no external I/O."""
from decimal import Decimal
from app.agents._et665_r356_common import attest,validate
AGENT_ID="domain.facebook_media_buyer_engine"
def describe_capabilities():
    return {"agent_id":AGENT_ID,"component":"monthly_cashflow","mode":"paper_only"}
def run_dry(payload=None):
    v=validate(payload)
    net=v["revenue"]-v["fixed_costs"]-v["variable_costs"]
    reserve=v["cash_balance"]
    output={"campaign_status":"PAUSED" if net<0 else "ELIGIBLE_FOR_REVIEW",
            "spend_cap":"0.00","available_cash_reserve":str(reserve),
            "optimization":"preserve_cash" if net<0 else "test_creative_offline",
            "roas":None,"roas_reason":"no_attributed_ad_spend_or_revenue",
            "ads_published":False}
    return attest(AGENT_ID,payload,output)
