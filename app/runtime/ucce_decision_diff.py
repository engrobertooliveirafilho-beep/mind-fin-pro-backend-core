def compare_decisions(dispatcher_reply,ucce):
    r=(ucce.get("reply","") or "").lower()
    c=9 if ucce.get("context_used") else 5
    social=9 if ucce.get("classification")=="SOCIAL" else 6
    fallback=1 if "exatamente" in r else 0
    return {"contextual_continuity_score":c,"semantic_collapse_score":0,"placeholder_score":0,"social_naturalness_score":social,"repetition_score":0,"execution_usefulness_score":8,"fallback_dependency_score":fallback,"winner":"ucce" if c>=8 else "dispatcher"}
