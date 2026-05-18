def require_consent(payload: dict) -> dict:
    consent = bool(payload.get("consent"))
    source = payload.get("source", "unknown")
    return {"consent_required": True, "consent_ok": consent, "source": source, "blocked": not consent}
