from app.runtime.followup_unified_resolver import resolve_followup

sender = "DEBUG_DUPLICATE"

print("RUN 1:", resolve_followup(sender, "como posso automatizar confinamento de boi?"))
print("RUN 2:", resolve_followup(sender, "como eu faço?"))
print("RUN 3:", resolve_followup(sender, "como eu faço?"))
