
from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
SCHEMA_SQL = """
create table if not exists eldora_messages(id bigserial primary key,user_id text,role text,content text,created_at timestamptz default now());
create table if not exists eldora_memory_facts(id bigserial primary key,user_id text,fact_key text,fact_value text,confidence float default 0.8,created_at timestamptz default now());
create table if not exists eldora_memory_edges(id bigserial primary key,user_id text,source_fact text,target_fact text,relation text,created_at timestamptz default now());
create table if not exists eldora_projects(id bigserial primary key,user_id text,project_name text,status text,metadata jsonb default '{}'::jsonb);
create table if not exists eldora_preferences(id bigserial primary key,user_id text,pref_key text,pref_value text);
create table if not exists eldora_emotional_signals(id bigserial primary key,user_id text,signal text,intensity text,created_at timestamptz default now());
create table if not exists eldora_conversation_arcs(id bigserial primary key,user_id text,current_arc text,state jsonb default '{}'::jsonb,updated_at timestamptz default now());
create table if not exists eldora_response_scores(id bigserial primary key,user_id text,score jsonb default '{}'::jsonb,created_at timestamptz default now());
"""
def save_message(user_id, role, content): return {"saved":True,"user_id":user_id,"role":role,"content":content}
def extract_memory_facts(message):
    facts=[]
    t=(message or "").lower()
    if "mind" in t: facts.append({"fact_key":"project","fact_value":"MIND","confidence":0.9})
    if "eldora" in t: facts.append({"fact_key":"agent","fact_value":"Eldora","confidence":0.9})
    if "roberto" in t: facts.append({"fact_key":"user_name","fact_value":"Roberto","confidence":0.95})
    return facts
def upsert_memory_fact(user_id, fact): return {"upserted":True,"user_id":user_id,"fact":fact}
def create_memory_edge(user_id, source_fact, target_fact, relation): return {"edge_created":True,"relation":relation}
def retrieve_relevant_memory(user_id, query): return {"facts":extract_memory_facts(query),"query":query}
def retrieve_user_profile(user_id): return {"user_id":user_id,"known_name":"Roberto","dominant_project":"MIND"}
def retrieve_project_context(user_id): return {"project":"MIND","agent":"Eldora","status":"cognitive_runtime_upgrade"}


# FINAL_IDENTITY_BLOCK
def __identity_guard_last_hop(answer,user_message=""):
    return enforce_no_identity_in_normal_chat(user_message,answer)
