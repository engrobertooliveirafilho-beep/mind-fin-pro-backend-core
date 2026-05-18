from fastapi import APIRouter
from app.persona.eldora_core import build_persona_context
from app.runtime.intent_router import route_intent
from app.memory.memory_graph import save_message,retrieve_relevant_memory,retrieve_user_profile,retrieve_project_context,SCHEMA_SQL
from app.runtime.internal_state import load_state,update_state,persist_state
from app.runtime.response_strategy import build_response_strategy
from app.runtime.response_builder import build_response
from app.runtime.quality_gate import rewrite_if_needed

router=APIRouter(prefix="/eldora/cognitive-runtime", tags=["eldora-cognitive-runtime"])

@router.get("/status")
def status():
    return {"STATUS_FINAL":"ELDORA_COGNITIVE_RUNTIME_IMPLEMENTED","schema_ready":True,"persona_core":True,"quality_gate":True}

@router.post("/respond")
def respond(payload:dict):
    user_id=payload.get("user_id","default")
    msg=payload.get("message","")
    save_message(user_id,"user",msg)
    intent=route_intent(msg)
    memory={"relevant":retrieve_relevant_memory(user_id,msg),"profile":retrieve_user_profile(user_id),"project":retrieve_project_context(user_id)}
    state=update_state(msg,intent,memory)
    persona=build_persona_context(user_id,state,memory)
    strategy=build_response_strategy(intent,state,memory)
    raw=build_response(msg,intent,memory,state,persona,strategy)
    final=rewrite_if_needed(raw,intent,persona,memory)
    save_message(user_id,"assistant",final["answer"])
    persist_state(user_id,state)
    return {"STATUS_FINAL":"ELDORA_COGNITIVE_RESPONSE_READY","intent":intent,"state":state,"strategy":strategy,"answer":final["answer"],"scores":final["scores"]}
