from pathlib import Path

p = Path("app/context_runtime/universal_domain_context.py")
s = p.read_text(encoding="utf-8")

insert = r'''
# P19P30B_UNIVERSAL_SUBJECT_ENGINE
STOPWORDS = {
    "quero", "como", "fazer", "para", "uma", "um", "de", "da", "do", "das", "dos",
    "me", "eu", "vc", "você", "voce", "preciso", "melhor", "mais", "sobre",
    "no", "na", "nos", "nas", "e", "ou", "a", "o", "as", "os", "qual", "quais",
    "são", "sao", "prossiga", "continue", "continua", "depois", "explique"
}

def subject_tokens(text: str):
    t = norm(text)
    raw = re.findall(r"[a-zà-ÿ0-9]{3,}", t)
    return [x for x in raw if x not in STOPWORDS][:12]

def discover_subject(text: str):
    t = norm(text)
    toks = subject_tokens(t)
    return {
        "active_subject": t[:160],
        "subject_tokens": toks,
        "subject_source": "universal_subject_engine"
    }
# /P19P30B_UNIVERSAL_SUBJECT_ENGINE
'''

if "P19P30B_UNIVERSAL_SUBJECT_ENGINE" not in s:
    s = s.replace("def extract_subject(text: str) -> str:", insert + "\n\ndef extract_subject(text: str) -> str:", 1)

s = s.replace(
'''    d = domain or detect_domain(text)
    if not d:
        return get(sid)

    data = _load()
    data[sid] = {
        "active_domain": d,
        "active_subject": extract_subject(text),
        "last_user_text": text or "",
        "followup_policy": "continue_same_domain",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
''',
'''    hinted = domain or detect_domain(text)
    subject = discover_subject(text)
    d = hinted if hinted and hinted != "general" else "subject"

    if not subject.get("subject_tokens"):
        return get(sid)

    data = _load()
    data[sid] = {
        "active_domain": d,
        "active_subject": subject["active_subject"],
        "subject_tokens": subject["subject_tokens"],
        "subject_source": subject["subject_source"],
        "last_user_text": text or "",
        "followup_policy": "continue_same_subject",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
''')

s = s.replace(
'''    d = detect_domain(t)
    if d:
        ctx = bind(sender, text, d)
''',
'''    d = detect_domain(t)
    if d:
        ctx = bind(sender, text, d if d != "general" else None)
''')

p.write_text(s, encoding="utf-8")
print("P19P30B_CONTEXT_PATCH_OK")
