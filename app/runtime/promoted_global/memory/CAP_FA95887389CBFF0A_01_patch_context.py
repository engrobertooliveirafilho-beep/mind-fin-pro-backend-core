from pathlib import Path

p = Path("app/context_runtime/universal_domain_context.py")
s = p.read_text(encoding="utf-8")

if "P19P30_UNIVERSAL_DOMAIN_DISCOVERY_ENGINE" not in s:
    s = s.replace(
'''def extract_subject(text: str) -> str:
    t = norm(text)
    return t[:160]
''',
'''# P19P30_UNIVERSAL_DOMAIN_DISCOVERY_ENGINE
STOPWORDS = {
    "quero", "como", "fazer", "para", "uma", "um", "de", "da", "do", "das", "dos",
    "me", "eu", "vc", "você", "voce", "preciso", "melhor", "mais", "sobre",
    "no", "na", "nos", "nas", "e", "ou", "a", "o", "as", "os"
}

def subject_tokens(text: str):
    t = norm(text)
    raw = re.findall(r"[a-zà-ÿ0-9]{3,}", t)
    return [x for x in raw if x not in STOPWORDS][:12]

def discover_domain(text: str) -> str:
    d = detect_domain(text)
    if d and d != "general":
        return d
    toks = subject_tokens(text)
    if len(toks) >= 1:
        return "discovered"
    return ""

def extract_subject(text: str) -> str:
    t = norm(text)
    return t[:160]
# /P19P30_UNIVERSAL_DOMAIN_DISCOVERY_ENGINE
'''
    )

    s = s.replace(
'''"active_subject": extract_subject(text),
        "last_user_text": text or "",
        "followup_policy": "continue_same_domain",
''',
'''"active_subject": extract_subject(text),
        "subject_tokens": subject_tokens(text),
        "domain_source": "hint" if d != "discovered" else "discovery",
        "last_user_text": text or "",
        "followup_policy": "continue_same_domain",
'''
    )

    s = s.replace(
'''    d = domain or detect_domain(text)
''',
'''    d = domain or discover_domain(text)
'''
    )

    s = s.replace(
'''    d = detect_domain(t)
''',
'''    d = discover_domain(t)
'''
    )

p.write_text(s, encoding="utf-8")
print("P19P30_CONTEXT_DISCOVERY_PATCH_OK")
