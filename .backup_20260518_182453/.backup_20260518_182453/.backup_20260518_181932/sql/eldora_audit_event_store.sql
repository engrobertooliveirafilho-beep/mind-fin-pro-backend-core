create table if not exists eldora_audit_events (
    id bigserial primary key,
    event_type text not null,
    actor text default 'system',
    payload jsonb default '{}'::jsonb,
    created_at timestamptz default now()
);

create table if not exists eldora_event_store (
    id bigserial primary key,
    topic text not null,
    payload jsonb default '{}'::jsonb,
    created_at timestamptz default now()
);
