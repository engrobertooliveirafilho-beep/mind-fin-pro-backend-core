from datetime import datetime, timezone

INTERNET_SIGNALS=[]

def internet_awareness(source:str, signal:str):
    item = {
        "source":source,
        "signal":signal,
        "awareness":"active",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    INTERNET_SIGNALS.append(item)

    return {
        "status":"ok",
        "signal":item
    }

def awareness_report():
    return {
        "status":"ok",
        "signals_total":len(INTERNET_SIGNALS),
        "signals":INTERNET_SIGNALS[-100:]
    }
