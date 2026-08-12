from app.runtime.followup_unified_resolver import resolve_followup

sender = "USER_123"

print(resolve_followup(sender, "como posso automatizar confinamento de boi?"))
print(resolve_followup(sender, "como eu faço?"))
print(resolve_followup(sender, "e depois?"))
print(resolve_followup(sender, "explique melhor"))
