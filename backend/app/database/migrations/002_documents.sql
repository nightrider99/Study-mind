create extension if not exists "vector";

create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  filename text not null,
  storage_path text not null default '',
  mime_type text,
  size_bytes bigint,
  page_count int,
  status text not null default 'processing',   -- processing | ready | failed
  error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists documents_user_created_idx
  on documents (user_id, created_at desc);

drop trigger if exists documents_updated_at on documents;
create trigger documents_updated_at before update on documents
  for each row execute function set_updated_at();

create table if not exists chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references documents(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  content text not null,
  chunk_index int not null,
  token_count int,
  embedding vector(768),
  created_at timestamptz not null default now()
);
create index if not exists chunks_document_idx on chunks (document_id);
create index if not exists chunks_user_idx on chunks (user_id);
create index if not exists chunks_embedding_idx
  on chunks using hnsw (embedding vector_cosine_ops);

alter table documents enable row level security;
alter table chunks enable row level security;

drop policy if exists "own documents" on documents;
create policy "own documents" on documents
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "own chunks" on chunks;
create policy "own chunks" on chunks
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Cosine similarity search.
-- NOTE: parameter is float8[] so PostgREST serializes cleanly, cast to vector inside.
create or replace function match_chunks(
  query_embedding float8[],
  match_user_id uuid,
  match_count int default 6,
  min_similarity float default 0.25
)
returns table (
  id uuid,
  document_id uuid,
  content text,
  similarity float
)
language sql stable
as $$
  with q as (
    select (
      '[' || array_to_string(query_embedding, ',') || ']'
    )::vector(768) as e
  )
  select c.id, c.document_id, c.content,
         1 - (c.embedding <=> q.e) as similarity
  from chunks c, q
  where c.user_id = match_user_id
    and c.embedding is not null
    and 1 - (c.embedding <=> q.e) >= min_similarity
  order by c.embedding <=> q.e
  limit match_count;
$$;
