from fastapi.testclient import TestClient

from app.main import app
from src.config import settings
from src.database import SessionLocal
from src.models import Case, User


def test_demo_users_can_browse_without_credentials():
    with TestClient(app, base_url="https://testserver") as client:
        assert client.get("/dashboard").status_code == 200
        assert client.get("/api/cases").status_code == 200


def test_production_users_are_redirected(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    with TestClient(app, base_url="https://testserver") as client:
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"].startswith("/login")
        assert client.get("/api/cases").status_code == 401


def login(client, email):
    response = client.post("/login", data={"email": email, "password": "carepulse-demo"}, follow_redirects=False)
    assert response.status_code == 303


def test_role_restriction_and_validation(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    with TestClient(app, base_url="https://testserver") as client:
        login(client, "agent@carepulse.demo")
        with SessionLocal() as db:
            agent = db.query(User).filter_by(email="agent@carepulse.demo").one()
            assigned_case = db.query(Case).filter_by(current_owner=agent.agent_id).first()
            assert assigned_case is not None
            assigned_case_id = assigned_case.case_id
        assert client.get("/dashboard").status_code == 403
        assert client.get(f"/agent/{assigned_case_id}").status_code == 200
        assert client.post("/api/events", json={"case_id": "CP-00006", "event_type": "CASE_OPENED", "metadata": "bad"}).status_code == 422


def test_agent_cannot_open_unassigned_assistant_case(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    with TestClient(app, base_url="https://testserver") as client:
        login(client, "agent@carepulse.demo")
        with SessionLocal() as db:
            agent = db.query(User).filter_by(email="agent@carepulse.demo").one()
            other_case = db.query(Case).filter(Case.current_owner != agent.agent_id).first()
            assert other_case is not None
            response = client.get(f"/assistant?case_id={other_case.case_id}&query=Give+me+a+summary")
        assert response.status_code == 403


def test_settings_and_action_tracking():
    with TestClient(app) as client:
        login(client, "admin@carepulse.demo")
        assert client.get("/settings").status_code == 200
        assert client.post("/api/settings/thresholds", json={"medium_threshold": 60, "high_threshold": 30}).status_code == 422
        action = client.post("/api/cases/CP-00006/actions", json={"action": "Send status update", "owner": "Agent-05", "status": "planned"})
        assert action.status_code == 200
        assert action.json()["status"] == "planned"


def test_unknown_page_has_friendly_error():
    with TestClient(app) as client:
        login(client, "cx.manager@carepulse.demo")
        response = client.get("/page-that-does-not-exist")
        assert response.status_code == 404
        assert "not available" in response.text.lower()
