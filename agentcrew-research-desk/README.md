# AgentCrew Research Desk

A multi-agent research assistant. Three local AI agents — **Researcher**, **Writer**,
and **Critic** — collaborate via [CrewAI](https://github.com/crewAIInc/crewAI) to
investigate a topic and return a sourced, edited report. Everything runs on a local
[Ollama](https://ollama.com) model, so no LLM API key is required.

![status](https://img.shields.io/badge/stack-Next.js%20%7C%20FastAPI%20%7C%20CrewAI%20%7C%20Ollama%20%7C%20Supabase-1B1F3B)

## How it works

```
 ┌─────────────┐     POST /research     ┌──────────────────┐      writes      ┌────────────┐
 │  Next.js UI │ ─────────────────────▶ │  FastAPI backend  │ ───────────────▶ │  Supabase  │
 │ (Vercel)    │ ◀───────────────────── │  (CrewAI + Ollama) │                 │  Postgres  │
 └─────────────┘   realtime subscribe   └──────────────────┘                  └────────────┘
```

1. You submit a topic from the dashboard.
2. FastAPI kicks off a background job and immediately returns a session row.
3. The crew runs sequentially: Researcher searches the web → Writer drafts a report →
   Critic reviews it.
4. The backend writes the final result to Supabase. The frontend is subscribed to
   Supabase Realtime, so the UI updates the moment the row changes — no polling.

## Project structure

```
backend/     FastAPI app + CrewAI agent definitions
frontend/    Next.js 14 (App Router) + Tailwind dashboard
supabase/    SQL schema (run once in the Supabase SQL editor)
```

## Local setup

### 1. Ollama
```bash
# install from https://ollama.com, then:
ollama pull llama3.1
ollama serve
```

### 2. Supabase
Create a project at supabase.com, then run `supabase/schema.sql` in the SQL editor.
Copy your project URL, anon key, and service role key.

### 3. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Supabase keys
uvicorn main:app --reload --port 8000
```

### 4. Frontend
```bash
cd frontend
npm install
cp .env.example .env.local   # fill in Supabase + API URL
npm run dev
```

Visit `http://localhost:3000`.

## Deploying

- **Frontend → Vercel.** Import the repo, set the root directory build via the included
  `vercel.json`, and add the three `NEXT_PUBLIC_*` env vars in the Vercel dashboard.
- **Backend → a host that allows long-running processes** (Render, Railway, Fly.io, or
  your own VM), since CrewAI jobs run in the background and Vercel's serverless
  functions time out too quickly for this. Point `NEXT_PUBLIC_API_URL` at that host.
- **Ollama** needs to run somewhere the backend can reach it — either the same host/VM,
  or a GPU box you control. For a fully-hosted demo without managing GPUs, you can swap
  `langchain_community.llms.Ollama` for any hosted-model LangChain LLM class with one
  line changed in `backend/agents.py`.

## Why this is a good portfolio piece

- Demonstrates agentic orchestration (CrewAI), not just a single prompt-response wrapper.
- Local-first inference (Ollama) — shows you can work outside hosted-API constraints.
- Realtime full-stack wiring (Supabase Realtime + Postgres + RLS), not just CRUD.
- Clean separation of concerns: stateless frontend, background-job backend, managed DB.

## License

MIT — use this as a template for your own agent projects.
