-- Run this in the Supabase SQL editor (or via `supabase db push`)

create table if not exists research_sessions (
  id uuid primary key default gen_random_uuid(),
  topic text not null,
  status text not null default 'running' check (status in ('running', 'completed', 'failed')),
  result text,
  created_at timestamptz not null default now()
);

-- Enable realtime so the frontend can subscribe to status changes
alter publication supabase_realtime add table research_sessions;

-- Row Level Security
alter table research_sessions enable row level security;

-- Public read access (demo app - tighten this for production with auth.uid())
create policy "Public read access"
  on research_sessions for select
  using (true);

-- Only the backend (service role key bypasses RLS) can insert/update.
-- No insert/update policy is created for anon/authenticated roles on purpose.
