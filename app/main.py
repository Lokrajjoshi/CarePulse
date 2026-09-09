import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, selectinload
from src.database import Base, SessionLocal, engine, get_db
from src.models import Case, Interaction
from src.config import settings
from src.metrics import customer_effort, first_response_minutes, resolution_minutes, silent_wait_minutes
from src.risk_engine import experience_risk
from src.care_actions import next_best_actions
from src.recovery import recovery_summary
from src.insights import business_recommendations
from src.sentiment import classify
from src.event_engine import EVENT_TYPES, ingest_event
from src.assistant import answer

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="CarePulse", description="Synthetic customer experience intervention and intelligence platform")
BASE = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")

@app.on_event("startup")
def bootstrap_demo_database():
    """Make an empty demo deployment usable after a free-host restart."""
    if settings.app_env != "demo":
        return
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if db.query(Case).count() == 0:
            subprocess.run([sys.executable, str(BASE.parent / "scripts" / "reset_demo.py")], check=True)
    finally:
        db.close()

class EventIn(BaseModel):
    case_id: str = Field(min_length=3, max_length=40)
    event_type: str
    actor_type: str = "system"
    actor_id: str | None = None
    message: str = ""
    event_timestamp: datetime | None = None
    metadata: dict = Field(default_factory=dict)

class AssistantIn(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    case_id: str | None = None

def load_case(db, case_id):
    case = db.query(Case).options(selectinload(Case.interactions), selectinload(Case.promises), selectinload(Case.interventions), selectinload(Case.feedback)).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")
    return case

def case_query(db):
    return db.query(Case).options(selectinload(Case.interactions), selectinload(Case.promises), selectinload(Case.interventions), selectinload(Case.feedback))

@app.get("/health")
def health():
    return {"status": "ok", "service": "carepulse"}

@app.get("/api/cases")
def cases(db: Session = Depends(get_db)):
    return [{"case_id": c.case_id, "industry": c.industry, "channel": c.channel, "issue_category": c.issue_category, "status": c.status} for c in db.query(Case).limit(100).all()]

@app.get("/api/cases/{case_id}")
def case_detail(case_id: str, db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    return {"case_id": c.case_id, "industry": c.industry, "channel": c.channel, "issue_category": c.issue_category, "priority": c.priority, "status": c.status, "silent_wait_minutes": silent_wait_minutes(c), "customer_effort": customer_effort(c), "risk": experience_risk(c), "recommendations": next_best_actions(c)}

@app.get("/api/cases/{case_id}/timeline")
def timeline(case_id: str, db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    return [{"timestamp": i.timestamp, "actor": i.actor_type, "message": i.message, "sentiment": i.sentiment_ground_truth} for i in sorted(c.interactions, key=lambda x: x.timestamp)]

@app.get("/api/cases/{case_id}/risk")
def risk(case_id: str, db: Session = Depends(get_db)):
    return experience_risk(load_case(db, case_id))

@app.get("/api/cases/{case_id}/recommendation")
def recommendation(case_id: str, db: Session = Depends(get_db)):
    return {"actions": next_best_actions(load_case(db, case_id))}

@app.get("/api/metrics/overview")
def overview(db: Session = Depends(get_db)):
    cs = case_query(db).all()
    feedback = [c.feedback for c in cs if c.feedback]
    promises = [p for c in cs for p in c.promises]
    return {"total_cases": len(cs), "csat": round(sum(f.csat_score for f in feedback) / len(feedback), 2), "dsat_pct": round(sum(f.dsat_flag for f in feedback) / len(feedback) * 100, 1), "nps": round(sum((f.recommendation_score >= 9) - (f.recommendation_score <= 6) for f in feedback) / len(feedback) * 100, 1), "avg_first_response_min": round(sum(first_response_minutes(c) for c in cs) / len(cs), 1), "avg_resolution_min": round(sum(resolution_minutes(c) for c in cs) / len(cs), 1), "avg_silent_wait_min": round(sum(silent_wait_minutes(c) for c in cs) / len(cs), 1), "promise_reliability": round(sum(p.promise_met for p in promises) / len(promises) * 100, 1), "high_risk_cases": sum(experience_risk(c)["band"] == "HIGH" for c in cs)}

@app.get("/api/analytics/recovery")
def recovery(db: Session = Depends(get_db)):
    return recovery_summary(case_query(db).all())

@app.get("/api/analytics/dsat-drivers")
def drivers(db: Session = Depends(get_db)):
    cs = case_query(db).all()
    def rate(items):
        return round(sum(c.feedback.dsat_flag for c in items if c.feedback) / len(items) * 100, 1) if items else 0
    groups = [("missed promise", [c for c in cs if any(not p.promise_met for p in c.promises)]), ("2+ transfers", [c for c in cs if sum(i.transfer_flag for i in c.interactions) >= 2]), ("repeat contact", [c for c in cs if c.feedback and c.feedback.repeat_contact_flag])]
    return [{"driver": name, "cases": len(items), "dsat_pct": rate(items)} for name, items in groups]

@app.get("/api/recommendations")
def recs(db: Session = Depends(get_db)):
    return business_recommendations(case_query(db).all())

@app.post("/api/events")
def create_event(payload: EventIn, db: Session = Depends(get_db)):
    case = load_case(db, payload.case_id)
    try:
        event = ingest_event(db, case, payload.event_type, payload.event_timestamp or datetime.utcnow(), payload.actor_type, payload.message, payload.metadata, payload.actor_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    refreshed = load_case(db, payload.case_id)
    return {"event_id": event.event_id, "event_type": event.event_type, "case_id": event.case_id, "risk": experience_risk(refreshed), "recommendations": next_best_actions(refreshed)}

@app.post("/api/assistant")
def assistant_api(payload: AssistantIn, db: Session = Depends(get_db)):
    case = load_case(db, payload.case_id) if payload.case_id else None
    result = answer(payload.query, case=case, overview_data=overview(db) if case is None else None)
    return result

@app.post("/api/cases/{case_id}/interactions")
def add_interaction(case_id: str, message: str = Form(...), db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    result = classify(message)
    db.add(Interaction(interaction_id=f"MAN-{case_id}-{len(c.interactions)+1}", case_id=case_id, timestamp=datetime.utcnow(), interaction_type="message", actor_type="agent", message=message, sentiment_ground_truth=result["label"], sentiment_score=result["score"], meaningful_update_flag=True, transfer_flag=False, repeat_explanation_flag=False))
    db.commit()
    return RedirectResponse(f"/agent/{case_id}", status_code=303)

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("home.html", {"request": request, "overview": overview(db)})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "overview": overview(db), "recovery": recovery(db), "drivers": drivers(db), "recs": recs(db)})

@app.get("/agent/{case_id}", response_class=HTMLResponse)
def agent(request: Request, case_id: str, db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    return templates.TemplateResponse("agent.html", {"request": request, "case": c, "risk": experience_risk(c), "effort": customer_effort(c), "wait": silent_wait_minutes(c), "actions": next_best_actions(c)})

@app.get("/customer/{case_id}", response_class=HTMLResponse)
def customer_view(request: Request, case_id: str, db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    return templates.TemplateResponse("customer.html", {"request": request, "case": c, "wait": silent_wait_minutes(c)})

@app.get("/cases", response_class=HTMLResponse)
def case_list(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("cases.html", {"request": request, "cases": db.query(Case).limit(30).all()})

def intelligence_context(db):
    cs = case_query(db).all()
    bands = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for c in cs:
        bands[experience_risk(c)["band"]] += 1
    return {"cases": cs, "bands": bands, "high_risk": sorted([c for c in cs if experience_risk(c)["band"] == "HIGH"], key=lambda c: experience_risk(c)["score"], reverse=True)[:12], "recovery": recovery_summary(cs), "overview": overview(db), "drivers": drivers(db), "recs": recs(db)}

@app.get("/story", response_class=HTMLResponse)
def story(request: Request, db: Session = Depends(get_db)):
    c = load_case(db, "CP-00006")
    return templates.TemplateResponse("story.html", {"request": request, "case": c, "risk": experience_risk(c), "wait": silent_wait_minutes(c), "effort": customer_effort(c), "actions": next_best_actions(c), "recovery": recovery_summary([c])})

@app.get("/journey", response_class=HTMLResponse)
def journey(request: Request, db: Session = Depends(get_db)):
    c = load_case(db, "CP-00006")
    return templates.TemplateResponse("journey.html", {"request": request, "case": c, "risk": experience_risk(c), "wait": silent_wait_minutes(c), "effort": customer_effort(c)})

@app.get("/risk-monitor", response_class=HTMLResponse)
def risk_monitor(request: Request, db: Session = Depends(get_db)):
    ctx = intelligence_context(db)
    return templates.TemplateResponse("risk_monitor.html", {"request": request, "experience_risk": experience_risk, **ctx})

@app.get("/sentiment", response_class=HTMLResponse)
def sentiment_page(request: Request, db: Session = Depends(get_db)):
    c = load_case(db, "CP-00006")
    return templates.TemplateResponse("sentiment.html", {"request": request, "case": c, "risk": experience_risk(c), "analysis": None})

@app.post("/sentiment/analyze", response_class=HTMLResponse)
def analyze_sentiment(request: Request, message: str = Form(...), source: str = Form("chat"), db: Session = Depends(get_db)):
    c = load_case(db, "CP-00006")
    return templates.TemplateResponse("sentiment.html", {"request": request, "case": c, "risk": experience_risk(c), "analysis": classify(message, source), "input_message": message, "input_source": source})

@app.get("/promise-wait", response_class=HTMLResponse)
def promise_wait(request: Request, db: Session = Depends(get_db)):
    ctx = intelligence_context(db)
    promises = [p for c in ctx["cases"] for p in c.promises]
    return templates.TemplateResponse("promise_wait.html", {"request": request, **ctx, "promises": promises})

@app.get("/dsat-drivers", response_class=HTMLResponse)
def dsat_drivers_page(request: Request, db: Session = Depends(get_db)):
    ctx = intelligence_context(db)
    return templates.TemplateResponse("dsat_drivers.html", {"request": request, **ctx})

@app.get("/recovery", response_class=HTMLResponse)
def recovery_page(request: Request, db: Session = Depends(get_db)):
    ctx = intelligence_context(db)
    return templates.TemplateResponse("recovery.html", {"request": request, **ctx})

@app.get("/recommendations", response_class=HTMLResponse)
def recommendations_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("recommendations.html", {"request": request, "recs": recs(db), "overview": overview(db)})

@app.get("/explorer", response_class=HTMLResponse)
def explorer(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("explorer.html", {"request": request, "cases": db.query(Case).limit(40).all(), "table_name": "Cases", "purpose": "One row per customer journey, including context, ownership, timing, and status."})

@app.get("/methodology", response_class=HTMLResponse)
def methodology(request: Request):
    return templates.TemplateResponse("methodology.html", {"request": request})

@app.get("/blueprint", response_class=HTMLResponse)
def blueprint(request: Request):
    return templates.TemplateResponse("blueprint.html", {"request": request})

@app.get("/assistant", response_class=HTMLResponse)
def assistant_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("assistant.html", {"request": request, "result": None, "case_id": "CP-00006"})

@app.post("/assistant", response_class=HTMLResponse)
def ask_assistant(request: Request, query: str = Form(...), case_id: str = Form("CP-00006"), db: Session = Depends(get_db)):
    case = load_case(db, case_id) if case_id else None
    return templates.TemplateResponse("assistant.html", {"request": request, "result": answer(query, case=case), "query": query, "case_id": case_id})

@app.get("/simulator", response_class=HTMLResponse)
def simulator(request: Request, db: Session = Depends(get_db)):
    case = load_case(db, "CP-00006")
    return templates.TemplateResponse("simulator.html", {"request": request, "case": case, "risk": experience_risk(case), "wait": silent_wait_minutes(case), "effort": customer_effort(case), "event_types": sorted(EVENT_TYPES), "notice": None})

@app.post("/simulator", response_class=HTMLResponse)
def simulator_emit(request: Request, event_type: str = Form(...), message: str = Form(""), db: Session = Depends(get_db)):
    case = load_case(db, "CP-00006")
    try:
        ingest_event(db, case, event_type, datetime.utcnow(), "customer" if "CUSTOMER" in event_type else "agent", message, {"channel": case.channel})
        notice = f"{event_type} ingested. Derived intelligence recalculated from the updated case."
    except ValueError as exc:
        notice = str(exc)
    case = load_case(db, "CP-00006")
    return templates.TemplateResponse("simulator.html", {"request": request, "case": case, "risk": experience_risk(case), "wait": silent_wait_minutes(case), "effort": customer_effort(case), "event_types": sorted(EVENT_TYPES), "notice": notice})
