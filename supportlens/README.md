# SupportLens

**Feedback deserves a follow-through.** A portfolio feedback and bug-investigation workspace built with FastAPI and vanilla JavaScript.

## Working workflow
Capture a report with reproduction evidence and impact → search and prioritize → inspect same-project duplicate suggestions → investigate → document a fix → verify it → export a Markdown release summary.

- Fictional examples are explicitly labeled; they are not live findings about other portfolio apps.
- Local browser persistence, non-destructive JSON backup import (existing IDs win), and a 200-report limit.
- Explainable Jaccard word-overlap duplicate suggestions; no automatic merges or AI claims.
- Fix evidence required before closure; local activity history and explicit verification.
- Responsive interface with accessible labels and keyboard focus styles.

## Run
From the repository root:

```sh
pip install fastapi uvicorn pydantic pytest httpx
uvicorn supportlens.main:app --port 8000
python -m pytest supportlens/test_supportlens.py -q
```

## Storage and scope
This is a single-browser portfolio MVP, not a multi-user support service. Records are kept in localStorage and are lost if browser data is cleared. Export backups. Duplicate analysis and backup validation send the workspace to the same-origin API; the API does not persist it or call external providers. Use only fictional/public-safe information on the public demo. Local history is user-editable, not an audit-grade log.

No billing, email, ticket-provider integration, authentication, attachments or multi-user database is implemented. Suggested future work: authenticated teams, durable shared storage, webhook intake, attachment security and integration tests.

## Upwork entry
**Title:** SupportLens — Customer Feedback & Bug Investigation Workspace

**Role:** Full-Stack Python Developer

**Description:** Built a feedback-to-fix workflow with validated report intake, impact-based prioritization, search, explainable duplicate suggestions, resolution evidence and verification. Added browser-local persistence, JSON backup/restore, Markdown release summaries and responsive UI. FastAPI validates data and computes same-project text similarity without paid AI services. Portfolio demo uses fictional examples.

**Skills:** Python, FastAPI, JavaScript, API Development, Web Application.

Demo: load fictional reports → detect the two similar mobile-menu reports → investigate one → document a resolution → mark fixed → verify → export release notes.
