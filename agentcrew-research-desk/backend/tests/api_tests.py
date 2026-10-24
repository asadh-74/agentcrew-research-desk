import sys
import types

import pytest
from fastapi.testclient import TestClient

import main


class MemoryQuery:
    def __init__(self, rows, action):
        self.rows = rows
        self.action = action
        self.filters = {}
        self.payload = None

    def insert(self, payload):
        self.action = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.action = "update"
        self.payload = payload
        return self

    def select(self, *_args):
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, *_args):
        return self

    def execute(self):
        if self.action == "insert":
            self.rows[self.payload["id"]] = dict(self.payload)
            return types.SimpleNamespace(data=[self.rows[self.payload["id"]]])
        matching = [row for row in self.rows.values() if all(row.get(k) == v for k, v in self.filters.items())]
        if self.action == "update":
            for row in matching:
                row.update(self.payload)
            return types.SimpleNamespace(data=matching)
        return types.SimpleNamespace(data=matching)


class MemorySupabase:
    def __init__(self):
        self.rows = {}

    def table(self, _name):
        return MemoryQuery(self.rows, "read")


@pytest.fixture
def client(monkeypatch):
    main.supabase = None
    return TestClient(main.app)


def test_health_reports_degraded_when_storage_is_missing(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["research_enabled"] is False


def test_missing_storage_rejects_jobs_instead_of_losing_them(client):
    response = client.post("/research", json={"topic": "Grid-scale batteries"})
    assert response.status_code == 503
    assert "storage is not configured" in response.json()["detail"]


@pytest.mark.parametrize("topic", ["  ", "abc", "x" * 301])
def test_topic_is_validated(client, topic):
    assert client.post("/research", json={"topic": topic}).status_code == 422


def test_job_is_saved_and_result_is_retrievable(client, monkeypatch):
    store = MemorySupabase()
    main.supabase = store

    class FakeCrew:
        def kickoff(self):
            return "## Findings\n\nA verifiable demo result."

    agents = types.ModuleType("agents")
    agents.build_crew = lambda _topic: FakeCrew()
    monkeypatch.setitem(sys.modules, "agents", agents)

    response = client.post("/research", json={"topic": "Battery recycling outlook"})
    assert response.status_code == 200
    session_id = response.json()["id"]
    assert store.rows[session_id]["status"] == "completed"
    assert "verifiable demo result" in store.rows[session_id]["result"]
    assert client.get(f"/sessions/{session_id}").json()["status"] == "completed"


def test_agent_failure_is_saved_without_exposing_exception(client, monkeypatch):
    store = MemorySupabase()
    main.supabase = store

    class BrokenCrew:
        def kickoff(self):
            raise RuntimeError("secret runtime details")

    agents = types.ModuleType("agents")
    agents.build_crew = lambda _topic: BrokenCrew()
    monkeypatch.setitem(sys.modules, "agents", agents)

    response = client.post("/research", json={"topic": "Battery recycling outlook"})
    session = store.rows[response.json()["id"]]
    assert session["status"] == "failed"
    assert "secret runtime details" not in session["result"]
    assert "Check the backend logs" in session["result"]
