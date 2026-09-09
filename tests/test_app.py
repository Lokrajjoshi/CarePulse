from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_required_pages_render():
    routes = [
        "/", "/dashboard", "/story", "/journey", "/risk-monitor", "/sentiment",
        "/agent/CP-00006", "/customer/CP-00006", "/promise-wait", "/dsat-drivers",
        "/recovery", "/recommendations", "/explorer", "/methodology", "/blueprint",
        "/assistant", "/simulator", "/docs",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, route


def test_health_and_assistant_api():
    assert client.get("/health").json()["status"] == "ok"
    response = client.post("/api/assistant", json={"case_id": "CP-00006", "query": "Why is this case high risk?"})
    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert "risk" in response.json()["answer"].lower()


def test_event_api_rejects_unknown_event_without_mutation():
    response = client.post("/api/events", json={"case_id": "CP-00006", "event_type": "NOT_A_REAL_EVENT"})
    assert response.status_code == 400
