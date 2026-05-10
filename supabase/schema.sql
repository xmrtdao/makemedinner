-- MakeMeDinner Supabase Schema
-- Vision & Multimodal AI track — AMD Developer Hackathon

-- Users pantry snapshot (last scanned ingredients)
create table if not exists pantries (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users(id) on delete cascade,
    ingredients jsonb not null default '[]',
    scanned_at timestamptz default now(),
    image_url text
);

-- Recipes database (seed + user-saved)
create table if not exists recipes (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    ingredients jsonb not null default '[]',
    steps jsonb not null default '[]',
    time_minutes int,
    difficulty text check (difficulty in ('Easy', 'Medium', 'Hard')),
    dietary_tags jsonb default '[]',
    source text default 'ai_generated',
    created_at timestamptz default now()
);

-- User recipe saves / ratings
create table if not exists user_recipes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users(id) on delete cascade,
    recipe_id uuid references recipes(id) on delete cascade,
    saved_at timestamptz default now(),
    rating int check (rating between 1 and 5),
    cooked_at timestamptz
);

-- TTS instruction cache (avoid regenerating same audio)
create table if not exists tts_cache (
    id uuid primary key default gen_random_uuid(),
    text_hash text unique not null,
    text_content text not null,
    audio_url text not null,
    voice text default 'default',
    created_at timestamptz default now()
);

-- Enable RLS
alter table pantries enable row level security;
alter table recipes enable row level security;
alter table user_recipes enable row level security;
alter table tts_cache enable row level security;

-- RLS policies
-- Pantries: users see only their own
 create policy "Users own pantries"
    on pantries for all
    using (user_id = auth.uid());

-- Recipes: public read, admin write
 create policy "Recipes public read"
    on recipes for select to anon, authenticated using (true);

-- User recipes: users see only their own
 create policy "Users own saved recipes"
    on user_recipes for all
    using (user_id = auth.uid());

-- TTS cache: public read (audio URLs are effectively public)
 create policy "TTS public read"
    on tts_cache for select to anon, authenticated using (true);

-- Indexes
 create index idx_pantries_user on pantries(user_id);
 create index idx_pantries_scanned on pantries(scanned_at desc);
 create index idx_recipes_tags on recipes using gin(dietary_tags);
 create index idx_recipes_ingredients on recipes using gin(ingredients);
 create index idx_tts_hash on tts_cache(text_hash);
