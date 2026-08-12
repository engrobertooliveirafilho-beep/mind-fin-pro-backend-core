create extension if not exists pgcrypto;
create extension if not exists vector;

create table if not exists p55a_animals (
    id uuid primary key default gen_random_uuid(),
    official_name text not null,
    aliases text[] default '{}',
    registry_number text,
    animal_type text default 'bull',
    sex text,
    country text,
    state text,
    city text,
    breeder text,
    owner text,
    company text,
    birth_year int,
    death_year int,
    life_status text default 'unknown',
    notes text,
    identity_key text unique,
    confidence_score numeric default 0,
    validation_status text default 'provisional',
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create table if not exists p55a_sources (
    id uuid primary key default gen_random_uuid(),
    source_url text not null,
    source_type text not null default 'OTHER',
    title text,
    publisher text,
    platform text,
    captured_at timestamptz default now(),
    evidence_hash text unique,
    raw_payload jsonb default '{}',
    confidence_score numeric default 0,
    validation_status text default 'provisional',
    created_at timestamptz default now()
);

create table if not exists p55a_animal_sources (
    animal_id uuid references p55a_animals(id) on delete cascade,
    source_id uuid references p55a_sources(id) on delete cascade,
    claim_type text default 'identity',
    claim_payload jsonb default '{}',
    confidence_score numeric default 0,
    primary key(animal_id, source_id, claim_type)
);

create table if not exists p55a_pedigree_edges (
    id uuid primary key default gen_random_uuid(),
    parent_id uuid references p55a_animals(id) on delete cascade,
    child_id uuid references p55a_animals(id) on delete cascade,
    relation text not null,
    generation_distance int default 1,
    evidence_source_id uuid references p55a_sources(id),
    confidence_score numeric default 0,
    validation_status text default 'provisional',
    created_at timestamptz default now(),
    unique(parent_id, child_id, relation)
);

create table if not exists p55a_media (
    id uuid primary key default gen_random_uuid(),
    animal_id uuid references p55a_animals(id) on delete cascade,
    source_id uuid references p55a_sources(id),
    url text not null,
    platform text,
    title text,
    channel_profile text,
    published_at timestamptz,
    duration_seconds numeric,
    event_name text,
    event_date date,
    event_location text,
    rider_name text,
    result text,
    bull_score numeric,
    rider_score numeric,
    ride_time_seconds numeric,
    buckoff boolean,
    metadata jsonb default '{}',
    confidence_score numeric default 0,
    validation_status text default 'provisional',
    created_at timestamptz default now()
);

create table if not exists p55a_biomechanics (
    id uuid primary key default gen_random_uuid(),
    media_id uuid references p55a_media(id) on delete cascade,
    animal_id uuid references p55a_animals(id) on delete cascade,
    jump_height numeric,
    jump_length numeric,
    horizontal_velocity numeric,
    vertical_velocity numeric,
    acceleration numeric,
    initial_explosion numeric,
    air_time numeric,
    kick_frequency numeric,
    kick_amplitude numeric,
    direction_changes int,
    angular_velocity numeric,
    estimated_torque numeric,
    estimated_kinetic_energy numeric,
    estimated_power numeric,
    unpredictability numeric,
    sporting_aggressiveness numeric,
    consistency numeric,
    difficulty numeric,
    biomechanics_score numeric,
    buckoff_pressure_score numeric,
    explosiveness_score numeric,
    spin_score numeric,
    kick_score numeric,
    difficulty_score numeric,
    consistency_score numeric,
    model_version text,
    confidence_score numeric default 0,
    created_at timestamptz default now()
);

create table if not exists p55a_judge_scores (
    id uuid primary key default gen_random_uuid(),
    media_id uuid references p55a_media(id) on delete cascade,
    animal_id uuid references p55a_animals(id) on delete cascade,
    official_bull_score numeric,
    mind_bull_score numeric,
    absolute_error numeric,
    percentage_error numeric,
    event_bias numeric,
    country_bias numeric,
    judge_bias numeric,
    style_bias numeric,
    explanation jsonb default '{}',
    model_version text,
    confidence_score numeric default 0,
    created_at timestamptz default now()
);

create table if not exists p55a_valuation_events (
    id uuid primary key default gen_random_uuid(),
    animal_id uuid references p55a_animals(id) on delete cascade,
    event_type text not null,
    event_date date,
    currency text default 'USD',
    amount numeric,
    semen_price numeric,
    embryo_price numeric,
    pregnancy_price numeric,
    breeding_fee numeric,
    shares_sold numeric,
    buyer text,
    seller text,
    auction_name text,
    source_id uuid references p55a_sources(id),
    raw_payload jsonb default '{}',
    confidence_score numeric default 0,
    validation_status text default 'provisional',
    created_at timestamptz default now()
);

create table if not exists p55a_reproduction_records (
    id uuid primary key default gen_random_uuid(),
    animal_id uuid references p55a_animals(id) on delete cascade,
    sire_id uuid references p55a_animals(id),
    dam_id uuid references p55a_animals(id),
    offspring_id uuid references p55a_animals(id),
    semen_available boolean,
    embryo_available boolean,
    pregnancy_available boolean,
    dna_available boolean,
    genomic_payload jsonb default '{}',
    reproductive_payload jsonb default '{}',
    confidence_score numeric default 0,
    validation_status text default 'provisional',
    created_at timestamptz default now()
);

create table if not exists p55a_country_rankings (
    id uuid primary key default gen_random_uuid(),
    country text not null,
    ranking_date date default current_date,
    strength numeric,
    spin numeric,
    explosion numeric,
    kick numeric,
    difficulty numeric,
    consistency numeric,
    buckoff_capacity numeric,
    genetic_production numeric,
    commercial_value numeric,
    pedigree_depth numeric,
    documented_volume numeric,
    global_score numeric,
    created_at timestamptz default now(),
    unique(country, ranking_date)
);

create table if not exists p55a_audit_logs (
    id uuid primary key default gen_random_uuid(),
    entity_type text not null,
    entity_id uuid,
    audit_type text not null,
    confidence_score numeric default 0,
    evidence_count int default 0,
    source_count int default 0,
    conflict_count int default 0,
    missing_fields text[] default '{}',
    contradictions jsonb default '[]',
    audit_status text default 'provisional',
    last_verified_at timestamptz default now(),
    created_at timestamptz default now()
);

create index if not exists idx_p55a_animals_identity_key on p55a_animals(identity_key);
create index if not exists idx_p55a_animals_name on p55a_animals using gin(to_tsvector('simple', official_name));
create index if not exists idx_p55a_sources_url on p55a_sources(source_url);
create index if not exists idx_p55a_media_animal on p55a_media(animal_id);
create index if not exists idx_p55a_pedigree_parent on p55a_pedigree_edges(parent_id);
create index if not exists idx_p55a_pedigree_child on p55a_pedigree_edges(child_id);
create index if not exists idx_p55a_valuation_animal on p55a_valuation_events(animal_id);
create index if not exists idx_p55a_audit_entity on p55a_audit_logs(entity_type, entity_id);
