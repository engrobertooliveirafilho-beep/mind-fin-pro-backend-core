from app.runtime.dialogue_state import (
    is_repeated,
    remember_response,
)

from app.runtime.conversational_reasoning import (
    update_dialogue_state,
)

from app.runtime.visible_response_layer import visible_reformulate
from app.runtime.real_humanization_runtime import real_humanization_runtime


def naturalize_response(
    answer: str,
    intent: dict,
    state: dict,
    autonomous: dict,
) -> str:

    text = str(answer or "").strip()

    if not text:
        return ""

    state = state if isinstance(state, dict) else {}
    autonomous = autonomous if isinstance(autonomous, dict) else {}

    user_id = state.get("user_id", "anonymous")

    message = str(
        state.get("last_unresolved_topic")
        or ""
    ).strip()

    context = {
        "social": state.get("social", {}),
        "emotion": state.get("emotion", {}),
        "relationship": state.get("relationship", {}),
        "state": state,
        "autonomous": autonomous,
    }

    try:

        humanized = real_humanization_runtime(
            message,
            text,
            context,
        )

        if isinstance(humanized, dict):

            candidate = str(
                humanized.get("answer")
                or ""
            ).strip()

            if candidate:
                text = candidate

    except Exception:
        pass

    if text and is_repeated(user_id, text):

        try:

            candidate = visible_reformulate(
                text,
                message,
                state.get("dominant_project", ""),
            )

            if candidate:
                text = str(candidate).strip()

        except Exception:
            pass

    if not text:
        return ""

    try:

        update_dialogue_state(
            user_id,
            message,
            text,
            claim=None,
            reasoning=None,
            confidence=0.90,
        )

    except Exception:
        pass

    try:
        remember_response(user_id, text)
    except Exception:
        pass

    return text