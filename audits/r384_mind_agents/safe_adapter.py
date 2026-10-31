"""Quarantined keyword-only adapter, with no external imports."""
def run_mind_talk_v2(user_id, input_text, metadata=None, *, execute):
    if not callable(execute) or not user_id or not input_text:
        raise ValueError("INVALID_INPUT")
    meta = metadata or {}
    result = execute(prompt=input_text, user_id=user_id, org_id=meta.get("org_id"), plan=meta.get("plan"), explicit_profile_id=meta.get("explicit_profile_id"), extra_context=meta)
    if not isinstance(result, dict) or not result.get("tools"):
        raise ValueError("NO_VERIFIED_TOOLS")
    for tool in result["tools"]:
        if tool.get("ok") is not True or tool.get("error") or tool.get("payload", {}).get("status") in ("stub", "noop", "error", "not_implemented"):
            raise ValueError("UNVERIFIED_TOOL")
    return result
