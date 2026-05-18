def run_autonomous_cognition_layer(user_id: str, message: str) -> dict:
    try:
        from app.memory.longitudinal_memory import remember_long_term, retrieve_longitudinal_context
        from app.runtime.user_goal_tracker import track_goal, active_goals
        from app.runtime.autonomous_planner import build_autonomous_plan
        from app.runtime.behavioral_patterns import detect_behavioral_patterns
        from app.runtime.conversation_evolution import evolve_conversation_arc
        memory = remember_long_term(user_id, message)
        context = retrieve_longitudinal_context(user_id, message)
        goal = track_goal(user_id, "evoluir MIND/Eldora para operação autônoma")
        goals = active_goals(user_id)
        plan = build_autonomous_plan(user_id, context)
        patterns = detect_behavioral_patterns(user_id, [message])
        arc = evolve_conversation_arc(user_id, message)
        return {"autonomous_ready": True, "memory": memory, "context": context, "goal": goal, "goals": goals, "plan": plan, "patterns": patterns, "arc": arc}
    except Exception as exc:
        return {"autonomous_ready": False, "error": str(exc)[:160]}
