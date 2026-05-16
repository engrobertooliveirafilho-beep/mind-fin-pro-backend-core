from datetime import datetime, time
def can_send(profile, now=None):
    now = now or datetime.utcnow()
    if profile.get("opt_out"): return False, "OPT_OUT"
    if profile.get("last_proactive_sent_at") and profile["last_proactive_sent_at"][:10] == now.date().isoformat(): return False, "DAILY_LIMIT"
    if now.hour < 8 or now.hour >= 22: return False, "QUIET_HOURS"
    return True, "OK"
