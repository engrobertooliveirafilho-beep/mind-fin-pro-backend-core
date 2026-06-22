from typing import Dict, Any

VERSION="P19P36W_CANARY_RUNTIME_VALIDATION"

def validate_canary_context(ctx: Dict[str, Any]) -> Dict[str, Any]:
    required = [
        "p19p36k_memory_shadow",
        "p19p36l_memory_fusion_shadow",
        "p19p36m_memory_fusion_advisor_shadow",
        "p19p36o_relationship_memory_shadow",
        "p19p36p_long_term_goal_shadow",
    ]
    present=[x for x in required if x in (ctx or {})]
    return {
        "required_count": len(required),
        "present_count": len(present),
        "missing": [x for x in required if x not in present],
        "canary_pass": len(present) >= 3,
        "mode": "SHADOW_ONLY",
        "version": VERSION,
    }
