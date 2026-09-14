from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
client.__enter__()
client.post("/login", data={"email": "cx.manager@carepulse.demo", "password": "carepulse-demo"})


def test_required_pages_render():
    routes = [
        "/", "/dashboard", "/story", "/journey", "/risk-monitor", "/sentiment",
        "/agent/CP-00006", "/customer/CP-00006", "/promise-wait", "/dsat-drivers",
        "/recovery", "/recommendations", "/explorer", "/insights", "/methodology", "/blueprint",
        "/assistant", "/simulator", "/docs",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, route


def test_sidebar_highlights_current_page():
    response = client.get("/risk-monitor")
    assert response.status_code == 200
    assert 'class="side-link is-active" href="/risk-monitor"' in response.text
    assert 'class="side-link is-active" href="/story"' not in response.text


def test_health_and_assistant_api():
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/favicon.ico").status_code == 200
    response = client.post("/api/assistant", json={"case_id": "CP-00006", "query": "Why is this case high risk?"})
    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert "risk" in response.json()["answer"].lower()


def test_assistant_prompt_links_return_grounded_answer():
    response = client.get("/assistant?query=Why+is+this+case+high+risk")
    assert response.status_code == 200
    assert "GROUNDED ANSWER" in response.text
    assert "CP-00006" in response.text


def test_event_api_rejects_unknown_event_without_mutation():
    response = client.post("/api/events", json={"case_id": "CP-00006", "event_type": "NOT_A_REAL_EVENT"})
    assert response.status_code == 400


def test_insights_filters_and_reports_are_consistent():
    response = client.get("/insights?days=365&team=Core+Support&channel=Chat")
    assert response.status_code == 200
    assert "Agent &amp; Team Insights" in response.text
    csv = client.get("/reports/cases.csv?days=365&team=Core+Support&channel=Chat")
    xlsx = client.get("/reports/analysis.xlsx?days=365&team=Core+Support&channel=Chat")
    pdf = client.get("/reports/executive.pdf?days=365&team=Core+Support&channel=Chat")
    agent_pdf = client.get("/reports/agent.pdf?days=365&agent=Agent-01")
    team_pdf = client.get("/reports/team.pdf?days=365&team=Core+Support")
    assert csv.status_code == 200 and csv.headers["content-type"].startswith("text/csv")
    assert xlsx.status_code == 200 and xlsx.content[:2] == b"PK"
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    assert agent_pdf.status_code == 200 and agent_pdf.content.startswith(b"%PDF")
    assert team_pdf.status_code == 200 and team_pdf.content.startswith(b"%PDF")
