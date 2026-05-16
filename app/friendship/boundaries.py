def can_send(profile):
    profile = profile or {}
    if profile.get("opt_out") is True:
        return False, "OPT_OUT"

    sent = int(profile.get("proactive_sent_today") or 0)
    limit = int(profile.get("daily_limit") or 1)
    if sent >= limit:
        return False, "DAILY_LIMIT"

    return True, "OK"
