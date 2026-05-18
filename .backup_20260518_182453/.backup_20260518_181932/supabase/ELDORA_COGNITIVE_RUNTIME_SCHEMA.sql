-- ELDORA COGNITIVE RUNTIME SCHEMA
create table if not exists eldora_messages(id bigserial primary key,user_id text,role text,content text,created_at timestamptz default now());
create table if not exists eldora_memory_facts(id bigserial primary key,user_id text,fact_key text,fact_value text,confidence float default 0.8,created_at timestamptz default now());
create table if not exists eldora_memory_edges(id bigserial primary key,user_id text,source_fact text,target_fact text,relation text,created_at timestamptz default now());
create table if not exists eldora_projects(id bigserial primary key,user_id text,project_name text,status text,metadata jsonb default '{}'::jsonb);
create table if not exists eldora_preferences(id bigserial primary key,user_id text,pref_key text,pref_value text);
create table if not exists eldora_emotional_signals(id bigserial primary key,user_id text,signal text,intensity text,created_at timestamptz default now());
create table if not exists eldora_conversation_arcs(id bigserial primary key,user_id text,current_arc text,state jsonb default '{}'::jsonb,updated_at timestamptz default now());
create table if not exists eldora_response_scores(id bigserial primary key,user_id text,score jsonb default '{}'::jsonb,created_at timestamptz default now());
