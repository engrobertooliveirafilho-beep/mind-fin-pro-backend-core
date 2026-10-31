"""Adapter layer to connect /mind/talk v2 with MIND agent runtime.

This module prepares a minimal, dict-based payload for agent_runtime.run_agent_turn_as_dict
so that the HTTP layer can switch to "MIND v2" via feature flag without breaking v1.
"""

from typing import Any, Dict, Optional

from .agent_runtime import run_agent_turn_as_dict


def run_mind_talk_v2(
    user_id: str,
    input_text: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a single MIND agent turn for the /mind/talk v2 pipeline.

    Parameters
    ----------
    user_id:
        Stable identifier of the end-user or agent session owner.
    input_text:
        Raw user message to be processed by the agent runtime.
    metadata:
        Optional extra information (tenant, plan, locale, creative context).

    Returns
    -------
    Dict[str, Any]
        Normalized agent turn result ready to be serialized as JSON.
    """
    payload: Dict[str, Any] = {
        "user_id": user_id,
        "input_text": input_text,
        "metadata": metadata or {},
    }
    return run_agent_turn_as_dict(payload)

