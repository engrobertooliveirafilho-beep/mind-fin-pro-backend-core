from pathlib import Path

p = Path("app/companionship/safe_recovery_adapter.py")
s = p.read_text(encoding="utf-8")

insert = r'''

# P19P36M_HOTFIX_EXCLUDE_CURRENT_MESSAGE_FROM_SCORING
def _p19p36m_hotfix_without_current_message(history: list, current_text: str):
    try:
        cur = str(current_text or "").strip().lower()
        if not cur:
            return list(history or [])
        cleaned = []
        removed = False
        for item in history or []:
            val = str(item or "").strip()
            if not removed and val.lower() == cur:
                removed = True
                continue
            cleaned.append(item)
        return cleaned
    except Exception:
        return list(history or [])
# /P19P36M_HOTFIX_EXCLUDE_CURRENT_MESSAGE_FROM_SCORING
'''

if "P19P36M_HOTFIX_EXCLUDE_CURRENT_MESSAGE_FROM_SCORING" not in s:
    s += insert

old = '''    scoring = score_memory_relevance(
        text=text,
        history=history,
        active_subject=ctx.get("active_subject") or "",
        active_domain=ctx.get("active_domain") or "",
    )
'''

new = '''    scoring_history = _p19p36m_hotfix_without_current_message(history, text)
    scoring = score_memory_relevance(
        text=text,
        history=scoring_history,
        active_subject=ctx.get("active_subject") or "",
        active_domain=ctx.get("active_domain") or "",
    )
    scoring["scoring_history_count"] = len(scoring_history)
    scoring["current_message_excluded"] = len(scoring_history) != len(history)
'''

if "current_message_excluded" not in s:
    if old not in s:
        raise SystemExit("score_memory_relevance block not found")
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("P19P36M_HOTFIX_PATCH_OK")
