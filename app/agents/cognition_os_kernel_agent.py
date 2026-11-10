"""ET665.R356 real isolated cognition.os_kernel_agent cashflow processing."""
from decimal import Decimal
from app.agents._et665_r356_common import attest,validate
AGENT_ID="cognition.os_kernel_agent"
def describe_capabilities():
    return {"agent_id":AGENT_ID,"component":"monthly_cashflow","mode":"paper_only"}
def run_dry(payload=None):
    v=validate(payload)
    net=v["revenue"]-v["fixed_costs"]-v["variable_costs"]
    burn=max(-net,Decimal("0"))
    output={"perception":{"revenue":str(v["revenue"]),"total_costs":str(v["fixed_costs"]+v["variable_costs"])},
            "memory":{"cash_balance":str(v["cash_balance"])},
            "simulation":{"net_cashflow":str(net),"runway_months":str((v["cash_balance"]/burn).quantize(Decimal("0.01"))) if burn else None},
            "plan":"preserve_cash" if net<0 else "maintain_reserve",
            "action":"NO_EXTERNAL_ACTION"}
    return attest(AGENT_ID,payload,output)
