import os
import uuid
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
log = logging.getLogger(__name__)

app = FastAPI(title="AgentCrew Research Desk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client | None = (
    create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    if SUPABASE_URL and SUPABASE_SERVICE_KEY
    else None
)


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=4, max_length=300)

    @field_validator("topic")
    @classmethod
    def nonblank_topic(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("topic is required")
        return value.strip()


class SessionOut(BaseModel):
    id: str
    topic: str
    status: str
    result: str | None = None
    created_at: str


def run_crew_job(session_id: str, topic: str):
    """Executed in the background: runs the crew and writes the result to Supabase."""
    try:
        # Import the large optional agent stack only when a research job is dispatched.
        from agents import build_crew

        crew = build_crew(topic)
        result = crew.kickoff()
        supabase.table("research_sessions").update(
            {"status": "completed", "result": str(result)}
        ).eq("id", session_id).execute()
    except Exception:  # noqa: BLE001
        log.exception("Research job %s failed", session_id)
        try:
            supabase.table("research_sessions").update(
                {"status": "failed", "result": "Research failed. Check the backend logs and confirm the model service is available."}
            ).eq("id", session_id).execute()
        except Exception:  # noqa: BLE001
            log.exception("Could not persist failure status for research job %s", session_id)


@app.post("/research", response_model=SessionOut)
def start_research(req: ResearchRequest, background_tasks: BackgroundTasks):
    if not supabase:
        raise HTTPException(503, "Research storage is not configured. Add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")

    session_id = str(uuid.uuid4())
    record = {
        "id": session_id,
        "topic": req.topic,
        "status": "running",
        "result": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        supabase.table("research_sessions").insert(record).execute()
    except Exception:  # noqa: BLE001
        log.exception("Could not save research session")
        raise HTTPException(503, "Could not save this inquiry. Check the database configuration and try again.") from None

    background_tasks.add_task(run_crew_job, session_id, req.topic)
    return record


@app.get("/sessions", response_model=list[SessionOut])
def list_sessions():
    if not supabase:
        raise HTTPException(503, "Research storage is not configured.")
    res = (
        supabase.table("research_sessions")
        .select("*")
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    return res.data


@app.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: str):
    if not supabase:
        raise HTTPException(503, "Research storage is not configured.")
    res = supabase.table("research_sessions").select("*").eq("id", session_id).execute()
    if not res.data:
        raise HTTPException(404, "session not found")
    return res.data[0]


@app.get("/health")
def health():
    ready = supabase is not None
    return {
        "status": "ok" if ready else "degraded",
        "research_enabled": ready,
        "supabase_configured": ready,
        "model": os.getenv("OLLAMA_MODEL", "llama3.1"),
    }
