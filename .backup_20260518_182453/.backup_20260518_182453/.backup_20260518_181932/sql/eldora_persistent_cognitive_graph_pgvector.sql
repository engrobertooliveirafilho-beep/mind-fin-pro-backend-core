create extension if not exists vector;

create table if not exists eldora_cognitive_memory (
    id bigserial primary key,
    tenant_id text default 'default',
    user_ref text default 'anonymous',
    content text not null,
    category text default 'general',
    embedding vector(16),
    priority int default 1,
    created_at timestamptz default now()
);

create index if not exists eldora_cognitive_memory_embedding_idx
on eldora_cognitive_memory using ivfflat (embedding vector_cosine_ops)
with (lists = 16);
