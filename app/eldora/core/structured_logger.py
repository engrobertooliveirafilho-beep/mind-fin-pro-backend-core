from datetime import datetime, timezone

def log(level: str, message: str, **fields):
    return {
        "level": level.upper(),
        "message": message,
        "fields": fields,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
