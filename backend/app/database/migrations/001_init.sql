create extension if not exists "pgcrypto";
create extension if not exists "vector";

create table if not exists notes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  content text not null default '',
  tags text[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists notes_user_updated_idx on notes (user_id, updated_at desc);

create or replace function set_updated_at() returns trigger as $$
begin new.updated_at = now(); return new; end;
$$ language plpgsql;

drop trigger if exists notes_updated_at on notes;
create trigger notes_updated_at before update on notes
  for each row execute function set_updated_at();

alter table notes enable row level security;
create policy "own notes" on notes
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
