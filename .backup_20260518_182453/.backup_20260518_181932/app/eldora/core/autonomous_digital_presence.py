from datetime import datetime, timezone

DIGITAL_PRESENCE=[]

def digital_presence(identity:str, platform:str):
    item = {
        "identity":identity,
        "platform":platform,
        "status":"online",
        "persistent":True,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    DIGITAL_PRESENCE.append(item)

    return {
        "status":"ok",
        "presence":item
    }

def presence_report():
    return {
        "status":"ok",
        "presence_total":len(DIGITAL_PRESENCE),
        "presence":DIGITAL_PRESENCE[-100:]
    }
