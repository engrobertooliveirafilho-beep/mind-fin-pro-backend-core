
from __future__ import annotations
from app.runtime.generic_conversation_state import update_conversation_state, progressive_answer, prevent_cross_topic

def global_topic_authority(answer:str,inbound:str="",sender_id:str="default")->str:
    state=update_conversation_state(sender_id,inbound)
    safe=prevent_cross_topic(answer,state)
    return progressive_answer(safe,state)
