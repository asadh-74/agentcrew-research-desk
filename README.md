# Research Desk Studio

An evidence-review workspace for collecting supplied source excerpts, organizing a cited brief, documenting limitations and recording a human decision.

## Current application

The supported application is the root `main.py` and `static/` directory. Run:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000. Render: Python runtime, repository root, build `pip install -r requirements.txt`, start `uvicorn main:app --host 0.0.0.0 --port $PORT`. Health endpoint: `/health`. Dockerfile is included. No database, local model, paid service or API key is required for the default workflow.

## Implemented

- Responsive desktop and mobile workspace with fictional examples.
- Validated server-side document generation through `/api/research`.
- Browser-local saved records, explicit approval, reviewer notes and revision numbers.
- Markdown export, JSON backup/restore with duplicate-ID handling, and browser Print / Save PDF.
- Optional protected Gemini summary, with schema checks and provider failure handling.
- Content Security Policy, escaped rendered text and no external scripts/fonts.
- Automated root-app tests, AgentCrew API lifecycle tests, JavaScript syntax checks and an AgentCrew production frontend build in GitHub Actions.

## Storage and privacy

Completed documents are stored in **this browser's localStorage**, not in a shared server database. They survive page reloads and server redeploys while browser data remains intact. They are not synced across browsers or devices. Clearing browser data removes them: export JSON backups to preserve or transfer work. Keep only public or fictional inputs in this public demo. The template API processes inputs but does not persist them server-side. Optional AI sends the supplied brief to Google only when explicitly requested with a valid access token.

Maximum 50 saved documents, 2 MB import limit. Backups are user-managed documents, not signed or tamper-proof audit logs. Approval is a local review status: no emails, payments, legal signatures or external actions occur.

## Optional AI configuration

Set `GEMINI_API_KEY` and a unique `AI_ACCESS_TOKEN` of at least 24 characters privately in the hosting environment. Optionally set `GEMINI_MODEL` (default `gemini-2.5-flash`). Never commit real values. Use the **Optional AI summary** button and enter the access token, not the model API key. The browser does not persist that token. Without configuration, the app returns a clear unavailable message and keeps the existing draft intact.

AI only adds a draft summary; it does not change source excerpts, prices or deliverable estimates. AI summaries need verification. The process-level cap is 10 AI calls per hour and resets on restart; this is not a distributed quota system. Use provider-level budgets before sharing access widely. Hosted real-provider responses have not been validated without private credentials; tests use a fake provider.

## Verification

18 root-app tests cover brief generation, source validation, GridWatch telemetry calculations and optional-AI protection. Seven AgentCrew API tests cover configuration readiness, input validation, session persistence and safe failure handling. The AgentCrew frontend also runs a clean production build in CI. Browser verification and deployment links are recorded in `UPWORK.md` after release.

## Portfolio scope

This is a functional portfolio workflow, not a production multi-tenant SaaS. Production deployment would add account authentication, durable server storage, role-based access, distributed limits, encrypted backups, monitoring and operational validation.

The separate **AgentCrew Research Desk** application is in `agentcrew-research-desk/`. It includes a Next.js interface, FastAPI API, CrewAI researcher/writer/critic workflow, Ollama model integration and Supabase session storage. It has a separate deployment setup from this root application; see its README for configuration. API lifecycle tests use mocked storage and model results, and the frontend has a credential-free production build. A live model run still requires your own Supabase and Ollama configuration. The root Research Desk Studio preserves supplied evidence; it does not independently browse, verify sources, or claim to execute multiple AI agents. Fictional example.com sources are clearly labeled.

## Public demo

https://asad-research-desk-studio.onrender.com/

Research Desk and ScopeCraft share a free Render service because the workspace service limit was reached. They have separate browser storage keys. ScopeCraft’s standalone source remains in `asadh-74/genai-Saas-Product`; the host repository contains a deployment copy in `scope_app/`. Changes to ScopeCraft must be synchronized to that deployment copy.

## AgentCrew application

From the repository root, enter `agentcrew-research-desk/` for the separate CrewAI app. Its API rejects new jobs until Supabase storage is configured, returns clear frontend errors, and records failed agent runs without returning backend exception details. The session schema allows public reads for the portfolio demo, so use only non-sensitive topics. Run `cd agentcrew-research-desk/backend && pip install -r requirements-dev.txt && pytest -q`, then `cd ../frontend && npm ci && npm run build` to validate its API and UI. The real CrewAI/Ollama path requires the full backend dependencies and a reachable model server.
