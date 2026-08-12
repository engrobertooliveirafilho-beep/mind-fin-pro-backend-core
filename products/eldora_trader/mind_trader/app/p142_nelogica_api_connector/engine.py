import os, json
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_ENV=[
    "NELOGICA_BASE_URL",
    "NELOGICA_API_KEY",
    "NELOGICA_API_SECRET",
    "NELOGICA_ENV"
]

B3_ASSETS=["WIN","WDO","IND","DOL","PETR4","VALE3","ITUB4","BBDC4","BBAS3","WEGE3","BOVA11"]

def env_status():
    return {k: bool(os.getenv(k)) for k in REQUIRED_ENV}

def connector_status():
    env=env_status()
    configured=all(env.values())
    return {
        "platform":"NELOGICA_API",
        "configured":configured,
        "env":env,
        "supported_assets":B3_ASSETS,
        "market_data_enabled":configured,
        "order_routing_enabled":False,
        "real_orders":"FORBIDDEN",
        "live":"FORBIDDEN",
        "real_broker":"DISABLED"
    }

def run():
    out=Path("reports/P14.2_NELOGICA_API_CONNECTOR")
    out.mkdir(parents=True,exist_ok=True)
    status={
        "STATUS":"P14.2_NELOGICA_API_CONNECTOR_FOUNDATION_IMPLEMENTED",
        "CONNECTOR":connector_status(),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"OBTAIN_NELOGICA_API_CREDENTIALS_AND_SANDBOX_DOCS",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"P14.2_nelogica_api_status.json").write_text(json.dumps(status,indent=2,ensure_ascii=False),encoding="utf-8")
    return status

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
