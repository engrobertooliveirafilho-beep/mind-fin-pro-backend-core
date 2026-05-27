def compare_decisions(dispatcher_reply,ucce_reply):
    live=(dispatcher_reply or "").strip()
    shadow=(ucce_reply.get("reply","") if isinstance(ucce_reply,dict) else "").strip()
    return {
        "contextual_continuity_score":5,
        "semantic_collapse_score":3,
        "placeholder_score":0 if shadow else 10,
        "social_naturalness_score":5,
        "repetition_score":0,
        "execution_usefulness_score":5,
        "fallback_dependency_score":2,
        "winner":"dispatcher",
        "promotion_candidate":False,
        "dispatcher_reply":live,
        "ucce_shadow_reply":shadow
    }
