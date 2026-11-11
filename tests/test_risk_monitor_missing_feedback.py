from types import SimpleNamespace

import app.main as main_module
from fastapi.testclient import TestClient

from app.main import app


def test_risk_monitor_renders_case_without_feedback(monkeypatch):
    case = SimpleNamespace(
        case_id="CP-NO-FEEDBACK",
        industry="Technology",
        issue_category="Access",
        current_owner="Agent-01",
        feedback=None,
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
    assert "CP-NO-FEEDBACK" in response.text
    assert "Not recorded" in response.text
