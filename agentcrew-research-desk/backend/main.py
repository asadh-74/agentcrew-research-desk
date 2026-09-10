import os
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

from agents import build_crew

load_dotenv()

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
    topic: str


class SessionOut(BaseModel):
    id: str
    topic: str
    status: str
    result: str | None = None
    created_at: str


def run_crew_job(session_id: str, topic: str):
    """Executed in the background: runs the crew and writes the result to Supabase."""
    try:
        crew = build_crew(topic)
        result = crew.kickoff()
        if supabase:
            supabase.table("research_sessions").update(
                {"status": "completed", "result": str(result)}
            ).eq("id", session_id).execute()
    except Exception as exc:  # noqa: BLE001
        if supabase:
            supabase.table("research_sessions").update(
                {"status": "failed", "result": f"Error: {exc}"}
            ).eq("id", session_id).execute()


@app.post("/research", response_model=SessionOut)
def start_research(req: ResearchRequest, background_tasks: BackgroundTasks):
    if not req.topic.strip():
        raise HTTPException(400, "topic is required")

    session_id = str(uuid.uuid4())
    record = {
        "id": session_id,
        "topic": req.topic,
        "status": "running",
        "result": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if supabase:
        supabase.table("research_sessions").insert(record).execute()

    background_tasks.add_task(run_crew_job, session_id, req.topic)
    return record


@app.get("/sessions", response_model=list[SessionOut])
def list_sessions():
    if not supabase:
        return []
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
        raise HTTPException(404, "not found")
    res = supabase.table("research_sessions").select("*").eq("id", session_id).execute()
    if not res.data:
        raise HTTPException(404, "session not found")
    return res.data[0]


@app.get("/health")
def health():
    return {"status": "ok", "supabase_connected": supabase is not None}
