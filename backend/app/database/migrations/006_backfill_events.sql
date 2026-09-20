-- Idempotent: guarded by NOT EXISTS on (user_id, kind, ref_id, created_at).
insert into study_events (user_id, kind, ref_id, value, created_at)
select
  qa.user_id, 'quiz_attempt', qa.quiz_id,
  case when qa.total > 0 then (qa.score::real / qa.total * 100.0) else 0 end,
  qa.created_at
from quiz_attempts qa
where not exists (
  select 1 from study_events se
  where se.user_id = qa.user_id
    and se.kind = 'quiz_attempt'
    and se.ref_id = qa.quiz_id
    and se.created_at = qa.created_at
);

insert into study_events (user_id, kind, ref_id, value, created_at)
select fr.user_id, 'card_review', fr.card_id, fr.rating::real, fr.reviewed_at
from flashcard_reviews fr
where not exists (
  select 1 from study_events se
  where se.user_id = fr.user_id
    and se.kind = 'card_review'
    and se.ref_id = fr.card_id
    and se.created_at = fr.reviewed_at
);
