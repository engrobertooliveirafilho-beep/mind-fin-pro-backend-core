from __future__ import annotations

P19P52_PROMOTION_MAP = {
    "program": "P19P52",
    "mode": "SHADOW_PROMOTION_MAP",
    "production_enabled": False,
    "runtime_mutation": False,
    "response_mutation": False,
    "priority_1": [
        "app/eldora/core/persistent_social_memory.py",
        "app/eldora/core/relational_cognition_engine.py",
        "app/memory/memory_graph.py",
        "app/persona/human_like_persona_pipeline.py",
        "app/friendship/friendship_profile.py",
    ],
    "priority_2": [
        "app/eldora/core/recursive_introspection_engine.py",
        "app/persona/persona_continuity_memory.py",
        "app/humanization/social_memory_provider.py",
        "app/humanization/social_pattern_extractor.py",
        "app/humanization/social_observation_layer.py",
    ],
}


def get_p19p52_promotion_map():
    return dict(P19P52_PROMOTION_MAP)
