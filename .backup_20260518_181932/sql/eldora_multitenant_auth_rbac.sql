create table if not exists eldora_tenants (
    id text primary key,
    name text not null,
    status text default 'active',
    created_at timestamptz default now()
);

create table if not exists eldora_users_auth (
    id bigserial primary key,
    tenant_id text references eldora_tenants(id),
    user_ref text not null,
    role text default 'user',
    created_at timestamptz default now()
);

create table if not exists eldora_policy_events (
    id bigserial primary key,
    tenant_id text default 'default',
    user_ref text default 'anonymous',
    role text default 'guest',
    action text not null,
    resource text default 'eldora',
    allowed boolean not null,
    created_at timestamptz default now()
);
