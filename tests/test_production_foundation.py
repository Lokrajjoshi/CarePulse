from types import SimpleNamespace

import app.main as main_module
from fastapi.testclient import TestClient

from app.main import app
from src.config import settings
from src.database import SessionLocal
from src.models import Case, User


def test_demo_users_can_browse_without_credentials():
    with TestClient(app, base_url="https://testserver") as client:
        assert client.get("/dashboard").status_code == 200
        assert client.get("/api/cases").status_code == 200


def test_risk_monitor_explains_the_next_action():
    with TestClient(app, base_url="https://testserver") as client:
        response = client.get("/risk-monitor")
        assert response.status_code == 200
        assert "highest-risk journeys first" in response.text
        assert "signals, owner, and recovery actions" in response.text


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


def test_agent_case_list_only_shows_owned_cases(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    with TestClient(app, base_url="https://testserver") as client:
        login(client, "agent@carepulse.demo")
        with SessionLocal() as db:
            agent = db.query(User).filter_by(email="agent@carepulse.demo").one()
            assigned_case = db.query(Case).filter_by(current_owner=agent.agent_id).first()
            other_case = db.query(Case).filter(Case.current_owner != agent.agent_id).first()
            assert assigned_case is not None
            assert other_case is not None
            assigned_case_id = assigned_case.case_id
            other_case_id = other_case.case_id

        response = client.get("/cases")

        assert response.status_code == 200
        assert assigned_case_id in response.text
        assert other_case_id not in response.text


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


def test_equal_risk_thresholds_are_rejected():
    with TestClient(app) as client:
        login(client, "admin@carepulse.demo")
        response = client.post(
            "/api/settings/thresholds",
            json={"medium_threshold": 40, "high_threshold": 40},
        )
        assert response.status_code == 422


def test_recovery_action_rejects_unknown_status():
    with TestClient(app) as client:
        login(client, "admin@carepulse.demo")
        response = client.post(
            "/api/cases/CP-00006/actions",
            json={"action": "Call customer", "owner": "Agent-05", "status": "done_later"},
        )
        assert response.status_code == 422


def test_unknown_page_has_friendly_error():
    with TestClient(app) as client:
        login(client, "cx.manager@carepulse.demo")
        response = client.get("/page-that-does-not-exist")
        assert response.status_code == 404
        assert "not available" in response.text.lower()


def test_login_rejects_an_external_next_path():
    with TestClient(app) as client:
        response = client.post(
            "/login",
            data={
                "email": "admin@carepulse.demo",
                "password": "carepulse-demo",
                "next": "https://outside.example",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert response.headers["location"] == "/dashboard"


def test_login_accepts_a_safe_internal_next_path():
    with TestClient(app) as client:
        response = client.post(
            "/login",
            data={
                "email": "admin@carepulse.demo",
                "password": "carepulse-demo",
                "next": "/insights?days=30",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert response.headers["location"] == "/insights?days=30"


def test_login_rejects_backslash_return_path():
    with TestClient(app) as client:
        response = client.post(
            "/login",
            data={
                "email": "admin@carepulse.demo",
                "password": "carepulse-demo",
                "next": "/\\outside.example",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert response.headers["location"] == "/dashboard"


def test_login_rejects_protocol_relative_return_path():
    with TestClient(app) as client:
        response = client.post(
            "/login",
            data={
                "email": "admin@carepulse.demo",
                "password": "carepulse-demo",
                "next": "//outside.example/path",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert response.headers["location"] == "/dashboard"


def test_login_rejects_control_character_return_path():
    with TestClient(app) as client:
        response = client.post(
            "/login",
            data={
                "email": "admin@carepulse.demo",
                "password": "carepulse-demo",
                "next": "/dashboard\nLocation: //outside.example",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert response.headers["location"] == "/dashboard"


def test_production_login_cookie_has_security_flags(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")

    with TestClient(app, base_url="https://testserver") as client:
        response = client.post(
            "/login",
            data={
                "email": "admin@carepulse.demo",
                "password": "carepulse-demo",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303

        cookie = response.headers["set-cookie"].lower()
        assert "httponly" in cookie
        assert "secure" in cookie
        assert "samesite=lax" in cookie


def test_logout_ends_production_session(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")

    with TestClient(app, base_url="https://testserver") as client:
        login(client, "admin@carepulse.demo")

        assert client.get("/dashboard").status_code == 200

        logout_response = client.post("/logout", follow_redirects=False)
        assert logout_response.status_code == 303
        assert logout_response.headers["location"] == "/login"

        dashboard_response = client.get("/dashboard", follow_redirects=False)
        assert dashboard_response.status_code == 303
        assert dashboard_response.headers["location"].startswith("/login")


def test_logout_expires_session_cookie(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")

    with TestClient(app, base_url="https://testserver") as client:
        login(client, "admin@carepulse.demo")

        response = client.post("/logout", follow_redirects=False)

        assert response.status_code == 303
        cookie = response.headers["set-cookie"].lower()
        assert "max-age=0" in cookie


def test_failed_login_does_not_set_session_cookie(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")

    with TestClient(app, base_url="https://testserver") as client:
        response = client.post(
            "/login",
            data={
                "email": "admin@carepulse.demo",
                "password": "wrong-password",
            },
            follow_redirects=False,
        )

        assert response.status_code == 401
        assert "set-cookie" not in response.headers


def test_login_normalizes_email_input(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")

    with TestClient(app, base_url="https://testserver") as client:
        response = client.post(
            "/login",
            data={
                "email": "  ADMIN@CAREPULSE.DEMO  ",
                "password": "carepulse-demo",
            },
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert response.headers["location"] == "/dashboard"


def test_inactive_user_cannot_login(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")

    with SessionLocal() as db:
        user = db.query(User).filter_by(email="admin@carepulse.demo").one()
        original_state = user.is_active
        user.is_active = False
        db.commit()

    try:
        with TestClient(app, base_url="https://testserver") as client:
            response = client.post(
                "/login",
                data={
                    "email": "admin@carepulse.demo",
                    "password": "carepulse-demo",
                },
                follow_redirects=False,
            )

            assert response.status_code == 401
            assert "set-cookie" not in response.headers
    finally:
        with SessionLocal() as db:
            user = db.query(User).filter_by(email="admin@carepulse.demo").one()
            user.is_active = original_state
            db.commit()


def test_inactive_user_existing_session_is_rejected(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")

    with TestClient(app, base_url="https://testserver") as client:
        login(client, "admin@carepulse.demo")

        with SessionLocal() as db:
            user = db.query(User).filter_by(email="admin@carepulse.demo").one()
            original_state = user.is_active
            user.is_active = False
            db.commit()

        try:
            response = client.get("/dashboard", follow_redirects=False)

            assert response.status_code == 303
            assert response.headers["location"].startswith("/login")
        finally:
            with SessionLocal() as db:
                user = db.query(User).filter_by(email="admin@carepulse.demo").one()
                user.is_active = original_state
                db.commit()


def test_risk_monitor_marks_missing_promise_separately(monkeypatch):
    case = SimpleNamespace(
        case_id="CP-TEST",
        industry="Technology",
        issue_category="Account access",
        current_owner="Agent-01",
        feedback=SimpleNamespace(final_sentiment="negative"),
        interactions=[],
        promises=[],
    )

    monkeypatch.setattr(
        main_module,
        "intelligence_context",
        lambda _db: {
            "bands": {"LOW": 0, "MEDIUM": 0, "HIGH": 1},
            "high_risk": [case],
        },
    )
    monkeypatch.setattr(main_module, "experience_risk", lambda _case: {"score": 80})
    monkeypatch.setattr(main_module, "silent_wait_minutes", lambda _case: 10)

    with TestClient(app) as client:
        response = client.get("/risk-monitor")

    assert response.status_code == 200
    assert "None recorded" in response.text


def test_risk_monitor_shows_missed_promise_count(monkeypatch):
    case = SimpleNamespace(
        case_id="CP-TEST", industry="Technology", issue_category="Account access",
        current_owner="Agent-01", feedback=SimpleNamespace(final_sentiment="negative"),
        interactions=[], promises=[SimpleNamespace(promise_met=False), SimpleNamespace(promise_met=False)],
    )
    monkeypatch.setattr(main_module, "intelligence_context", lambda _db: {"bands": {"LOW": 0, "MEDIUM": 0, "HIGH": 1}, "high_risk": [case]})
    monkeypatch.setattr(main_module, "experience_risk", lambda _case: {"score": 80})
    monkeypatch.setattr(main_module, "silent_wait_minutes", lambda _case: 10)
    with TestClient(app) as client:
        response = client.get("/risk-monitor")
    assert response.status_code == 200
    assert "2 missed" in response.text
