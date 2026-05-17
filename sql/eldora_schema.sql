create table if not exists eldora_users(
id uuid primary key,
created_at timestamptz default now()
);

create table if not exists eldora_memory(
id uuid primary key,
user_id uuid,
content text,
created_at timestamptz default now()
);
