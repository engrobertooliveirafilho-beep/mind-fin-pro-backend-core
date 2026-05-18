import re, hashlib, time

def normalize_phone_e164(phone: str, default_country="+55") -> str:
    digits = re.sub(r"\D+", "", phone or "")
    if not digits:
        raise ValueError("empty_phone")
    if digits.startswith("55") and len(digits) >= 12:
        return "+" + digits
    if len(digits) in (10, 11):
        return default_country + digits
    if phone.startswith("+"):
        return "+" + digits
    raise ValueError("invalid_phone")

def resolve_or_create_user(phone: str, name: str | None = None) -> dict:
    e164 = normalize_phone_e164(phone)
    uid = hashlib.sha256(e164.encode()).hexdigest()[:24]
    return {"user_id": uid, "phone_e164": e164, "name": name, "created_or_resolved": True}

def export_user_data(user_id: str) -> dict:
    return {"user_id": user_id, "export_ready": True, "format": "json"}

def delete_user_data(user_id: str) -> dict:
    return {"user_id": user_id, "delete_requested": True, "hard_delete": False, "timestamp": int(time.time())}
