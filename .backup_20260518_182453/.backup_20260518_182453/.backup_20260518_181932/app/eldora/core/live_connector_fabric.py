from datetime import datetime, timezone

CONNECTORS=[]

def register_connector(platform:str, capability:str):
    item = {
        "platform":platform,
        "capability":capability,
        "status":"connected",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    CONNECTORS.append(item)

    return {
        "status":"ok",
        "connector":item
    }

def connector_report():
    return {
        "status":"ok",
        "connectors_total":len(CONNECTORS),
        "connectors":CONNECTORS[-100:]
    }
