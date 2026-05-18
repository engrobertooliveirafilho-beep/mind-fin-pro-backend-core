def self_reflect(response, scores):
    return {"reflection_ready": True, "improve_next": scores.get("generic_response_score", 1) > 0.10}
