-- ============ quizzes ============
create table if not exists quizzes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  difficulty text not null default 'medium',
  document_ids uuid[] not null default '{}',
  note_ids uuid[] not null default '{}',
  created_at timestamptz not null default now()
);
create index if not exists quizzes_user_created_idx on quizzes (user_id, created_at desc);
alter table quizzes enable row level security;
drop policy if exists "own quizzes" on quizzes;
create policy "own quizzes" on quizzes
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists quiz_questions (
  id uuid primary key default gen_random_uuid(),
  quiz_id uuid not null references quizzes(id) on delete cascade,
  order_index int not null,
  question text not null,
  options jsonb not null,
  correct_index int not null,
  explanation text
);
create index if not exists quiz_questions_quiz_idx on quiz_questions (quiz_id, order_index);
-- no RLS here: accessed only via quizzes ownership check in the API

create table if not exists quiz_attempts (
  id uuid primary key default gen_random_uuid(),
  quiz_id uuid not null references quizzes(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  score int not null,
  total int not null,
  answers jsonb not null default '[]',
  created_at timestamptz not null default now()
);
create index if not exists quiz_attempts_user_idx on quiz_attempts (user_id, created_at desc);
alter table quiz_attempts enable row level security;
drop policy if exists "own attempts" on quiz_attempts;
create policy "own attempts" on quiz_attempts
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ============ flashcard decks ============
create table if not exists decks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  document_ids uuid[] not null default '{}',
  note_ids uuid[] not null default '{}',
  created_at timestamptz not null default now()
);
create index if not exists decks_user_created_idx on decks (user_id, created_at desc);
alter table decks enable row level security;
drop policy if exists "own decks" on decks;
create policy "own decks" on decks
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists flashcards (
  id uuid primary key default gen_random_uuid(),
  deck_id uuid not null references decks(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  front text not null,
  back text not null,
  ease real not null default 2.5,
  interval_days real not null default 0,
  reps int not null default 0,
  lapses int not null default 0,
  due_at timestamptz not null default now(),
  last_reviewed_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists flashcards_deck_idx on flashcards (deck_id);
create index if not exists flashcards_due_idx on flashcards (user_id, due_at);
alter table flashcards enable row level security;
drop policy if exists "own cards" on flashcards;
create policy "own cards" on flashcards
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table if not exists flashcard_reviews (
  id uuid primary key default gen_random_uuid(),
  card_id uuid not null references flashcards(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  rating int not null,
  reviewed_at timestamptz not null default now()
);
create index if not exists reviews_user_idx on flashcard_reviews (user_id, reviewed_at desc);
alter table flashcard_reviews enable row level security;
drop policy if exists "own reviews" on flashcard_reviews;
create policy "own reviews" on flashcard_reviews
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
