from datetime import datetime, UTC
_MEMORY={}
def get_state(sender_id:str):
    return _MEMORY.setdefault(sender_id,{
        "sender_id":sender_id,"last_topic":None,"last_problem":None,"last_goal":None,"last_user_question":None,
        "last_assistant_reply":None,"last_meaningful_reply":None,"last_open_task":None,"open_loop":False,
        "conversation_depth":0,"intent":None,"previous_intent":None,"frustration_signal":False,
        "continuity_anchor":None,"unresolved_error":None,"updated_at":datetime.now(UTC).isoformat()
    })
def save_state(sender_id:str,state:dict):
    state["updated_at"]=datetime.now(UTC).isoformat()
    _MEMORY[sender_id]=state
