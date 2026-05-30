def subject_alias(subject:str)->str:
    s=(subject or "").strip()

    if not s:
        return ""

    s=s.lower()

    if "cb" in s or "moto" in s or "yamaha" in s or "honda" in s or "bmw" in s:
        return "essa moto"

    if "carro" in s or "toyota" in s or "honda civic" in s:
        return "esse carro"

    return "isso"
