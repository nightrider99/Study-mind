create table if not exists study_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  kind text not null,           -- 'quiz_attempt' | 'card_review' | 'doc_upload'
  ref_id uuid,
  value real,                   -- quiz: percent score; review: rating; upload: null
  created_at timestamptz not null default now()
);
create index if not exists study_events_user_created_idx
  on study_events (user_id, created_at desc);
create index if not exists study_events_user_kind_idx
  on study_events (user_id, kind, created_at desc);

alter table study_events enable row level security;
drop policy if exists "own events" on study_events;
create policy "own events" on study_events
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Daily aggregates for the last N days, zero-filled.
create or replace function progress_timeline(
  p_user_id uuid,
  p_days int default 30
)
returns table (
  day date,
  quiz_attempts int,
  cards_reviewed int,
  avg_score real
)
language sql stable
as $$
  with days as (
    select generate_series(
      (current_date - (p_days - 1)), current_date, interval '1 day'
    )::date as day
  ),
  ev as (
    select
      (created_at at time zone 'utc')::date as day,
      kind,
      value
    from study_events
    where user_id = p_user_id
      and created_at >= (current_date - (p_days - 1))
  )
  select
    d.day,
    coalesce(count(*) filter (where ev.kind = 'quiz_attempt'), 0)::int,
    coalesce(count(*) filter (where ev.kind = 'card_review'), 0)::int,
    coalesce(avg(ev.value) filter (where ev.kind = 'quiz_attempt'), 0)::real
  from days d
  left join ev on ev.day = d.day
  group by d.day
  order by d.day;
$$;
