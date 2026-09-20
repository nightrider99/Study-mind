create table if not exists chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null default 'New chat',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists chat_sessions_user_idx
  on chat_sessions (user_id, updated_at desc);
alter table chat_sessions enable row level security;
drop policy if exists "own chat sessions" on chat_sessions;
create policy "own chat sessions" on chat_sessions
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references chat_sessions(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('user','assistant')),
  content text not null,
  sources jsonb,
  created_at timestamptz not null default now()
);
create index if not exists chat_messages_session_idx
  on chat_messages (session_id, created_at);
alter table chat_messages enable row level security;
drop policy if exists "own chat messages" on chat_messages;
create policy "own chat messages" on chat_messages
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop trigger if exists chat_sessions_updated_at on chat_sessions;
create trigger chat_sessions_updated_at before update on chat_sessions
  for each row execute function set_updated_at();
