create table if not exists eldora_users (
  id text primary key,
  phone_e164 text unique,
  name text,
  created_at timestamptz default now()
);

create table if not exists eldora_consents (
  id bigserial primary key,
  user_id text references eldora_users(id),
  consent_type text not null,
  granted boolean not null,
  source text,
  created_at timestamptz default now()
);

create table if not exists eldora_events (
  id bigserial primary key,
  tenant_id text,
  user_id text,
  event_type text not null,
  payload jsonb default '{}'::jsonb,
  idempotency_key text unique,
  created_at timestamptz default now()
);

create table if not exists eldora_worker_dlq (
  id bigserial primary key,
  stream text not null,
  event_id text,
  error text,
  payload jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);
