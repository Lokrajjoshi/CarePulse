import logging
import json
import subprocess
import sys
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session, selectinload
from src.database import Base, SessionLocal, engine, get_db
from src.models import Agent, AuditLog, Case, Customer, Interaction, Intervention, Organization, User
from src.config import settings
from src.auth import COOKIE_NAME, hash_password, make_session, read_session, verify_password
from src.tenant import current_organization_id, current_risk_thresholds, organization_id
from src.metrics import customer_effort, first_response_minutes, resolution_minutes, silent_wait_minutes
from src.risk_engine import experience_risk
from src.care_actions import next_best_actions
from src.recovery import recovery_summary
from src.insights import business_recommendations
from src.sentiment import classify
from src.event_engine import EVENT_TYPES, ingest_event
from src.assistant import answer
from src.analytics import Filters, apply_filters, metrics_for_cases, recommendations_for_cases, agent_rows, team_rows, monthly_rows, comparison_metrics
from app.services.report_service import csv_bytes, xlsx_bytes, pdf_bytes

logging.basicConfig(level=logging.INFO)
@asynccontextmanager
async def lifespan(_app):
    bootstrap_demo_database()
    yield

app = FastAPI(title="CarePulse", description="Synthetic customer experience intervention and intelligence platform", lifespan=lifespan)
BASE = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")

PUBLIC_PATHS = {"/", "/login", "/health", "/favicon.ico", "/docs", "/openapi.json", "/redoc"}
ROLE_RULES = {
    "/dashboard": {"admin", "cx_manager", "business_manager"},
    "/insights": {"admin", "cx_manager", "business_manager"},
    "/recommendations": {"admin", "cx_manager", "business_manager"},
    "/risk-monitor": {"admin", "cx_manager", "business_manager"},
    "/dsat-drivers": {"admin", "cx_manager", "business_manager"},
    "/promise-wait": {"admin", "cx_manager", "business_manager"},
    "/recovery": {"admin", "cx_manager", "business_manager"},
    "/explorer": {"admin", "cx_manager", "business_manager"},
    "/simulator": {"admin", "cx_manager"},
    "/agent": {"admin", "cx_manager", "business_manager", "agent"},
    "/customer": {"admin", "cx_manager", "business_manager", "agent", "customer"},
    "/reports": {"admin", "cx_manager", "business_manager"},
    "/api/events": {"admin", "cx_manager", "agent"},
    "/api/cases": {"admin", "cx_manager", "business_manager", "agent", "customer"},
    "/api/metrics": {"admin", "cx_manager", "business_manager"},
    "/api/analytics": {"admin", "cx_manager", "business_manager"},
    "/api/recommendations": {"admin", "cx_manager", "business_manager"},
    "/assistant": {"admin", "cx_manager", "business_manager", "agent", "customer"},
    "/api/assistant": {"admin", "cx_manager", "business_manager", "agent", "customer"},
    "/settings": {"admin"},
    "/api/settings": {"admin"},
}

def is_public_path(path: str) -> bool:
    return path in PUBLIC_PATHS or path.startswith("/static/")

def required_roles(path: str):
    for prefix, roles in ROLE_RULES.items():
        if path == prefix or path.startswith(prefix + "/"):
            return roles
    return None

@app.middleware("http")
async def session_gate(request: Request, call_next):
    request.state.user = None
    if is_public_path(request.url.path):
        return await call_next(request)
    with SessionLocal() as db:
        if settings.app_env == "demo":
            organization = db.query(Organization).filter_by(slug="carepulse-demo").first()
            org_token = current_organization_id.set(organization.organization_id if organization else "ORG-DEMO")
            threshold_token = current_risk_thresholds.set((organization.risk_medium_threshold, organization.risk_high_threshold) if organization else (30, 60))
            try:
                return await call_next(request)
            finally:
                current_organization_id.reset(org_token)
                current_risk_thresholds.reset(threshold_token)
        user_id = read_session(request.cookies.get(COOKIE_NAME))
        user = db.get(User, user_id) if user_id else None
        if not user or not user.is_active:
            if request.url.path.startswith("/api/"):
                return JSONResponse({"error": "Authentication required.", "status_code": 401}, status_code=401)
            next_path = str(request.url.path)
            if request.url.query:
                next_path += "?" + request.url.query
            return RedirectResponse(f"/login?next={next_path}", status_code=303)
        roles = required_roles(request.url.path)
        if roles and user.role not in roles:
            if request.url.path.startswith("/api/"):
                return JSONResponse({"error": "You do not have permission for this resource.", "status_code": 403}, status_code=403)
            return templates.TemplateResponse(request, "error.html", {"request": request, "title": "That workspace is restricted", "message": "Your current role does not have access to this view. Return to your workspace or sign in with an approved role."}, status_code=403)
        if request.url.path.startswith("/agent/") and user.role == "agent":
            case_id = request.url.path.split("/", 2)[-1]
            case = db.query(Case).filter(Case.case_id == case_id, Case.organization_id == user.organization_id).first()
            if not case or case.current_owner != user.agent_id:
                return templates.TemplateResponse(request, "error.html", {"request": request, "title": "This case is outside your queue", "message": "Agents can open cases assigned to them. Ask a CX manager to reassign this case if you need access."}, status_code=403)
        if request.url.path.startswith("/customer/") and user.role == "customer":
            case_id = request.url.path.split("/", 2)[-1]
            case = db.query(Case).filter(Case.case_id == case_id, Case.organization_id == user.organization_id).first()
            if not case or case.customer_id != user.customer_id:
                return templates.TemplateResponse(request, "error.html", {"request": request, "title": "This case is not yours to view", "message": "Customers can only access their own case information."}, status_code=403)
        request.state.user = user
        db.add(AuditLog(organization_id=user.organization_id, user_id=user.user_id, action="access", resource=request.url.path, metadata_json="{}"))
        db.commit()
        organization = db.get(Organization, user.organization_id)
        org_token = current_organization_id.set(user.organization_id)
        threshold_token = current_risk_thresholds.set((organization.risk_medium_threshold, organization.risk_high_threshold) if organization else (30, 60))
        try:
            return await call_next(request)
        finally:
            current_organization_id.reset(org_token)
            current_risk_thresholds.reset(threshold_token)

@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": str(exc.detail), "status_code": exc.status_code}, status_code=exc.status_code)
    title = "This case or page is not available" if exc.status_code == 404 else "We could not open that page"
    message = "The link may be outdated, or the requested case is not in this demo dataset." if exc.status_code == 404 else "CarePulse could not complete this request. Please try again in a moment."
    return templates.TemplateResponse(request, "error.html", {"request": request, "title": title, "message": message}, status_code=exc.status_code)

@app.exception_handler(StarletteHTTPException)
async def starlette_http_error(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": str(exc.detail), "status_code": exc.status_code}, status_code=exc.status_code)
    title = "This page is not available" if exc.status_code == 404 else "We could not open that page"
    message = "The link may be outdated. Return to the CarePulse home page and choose another workspace view." if exc.status_code == 404 else "CarePulse could not complete this request. Please try again in a moment."
    return templates.TemplateResponse(request, "error.html", {"request": request, "title": title, "message": message}, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": "The request data is invalid.", "status_code": 422}, status_code=422)
    return templates.TemplateResponse(request, "error.html", {"request": request, "title": "Please check the information", "message": "One or more values were not accepted. Please review the form and try again."}, status_code=422)

@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logging.exception("Unhandled request error: %s", exc)
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": "CarePulse could not complete the request.", "status_code": 500}, status_code=500)
    return templates.TemplateResponse(request, "error.html", {"request": request, "title": "CarePulse could not complete that", "message": "The service encountered a temporary problem. Please try again, or return to the home page."}, status_code=500)

def bootstrap_demo_database():
    """Make an empty demo deployment usable after a free-host restart."""
    Base.metadata.create_all(engine)
    _ensure_legacy_columns()
    db = SessionLocal()
    try:
        organization = db.query(Organization).filter_by(slug="carepulse-demo").first()
        if not organization:
            organization = Organization(organization_id="ORG-DEMO", slug="carepulse-demo", name="CarePulse Demo Organisation")
            db.add(organization)
            db.commit()
        _assign_existing_records(db, organization.organization_id)
        if settings.app_env == "demo":
            _seed_demo_users(db, organization.organization_id)
        if settings.app_env == "demo" and db.query(Case).count() == 0:
            subprocess.run([sys.executable, str(BASE.parent / "scripts" / "reset_demo.py")], check=True)
            _assign_existing_records(db, organization.organization_id)
            _seed_demo_users(db, organization.organization_id)
    finally:
        db.close()

def _ensure_legacy_columns():
    """Add nullable tenant columns to an older local demo database once."""
    inspector = inspect(engine)
    with engine.begin() as connection:
        additions = {
            "customers": [("organization_id", "VARCHAR")],
            "agents": [("organization_id", "VARCHAR")],
            "cases": [("organization_id", "VARCHAR")],
            "organizations": [("risk_medium_threshold", "INTEGER"), ("risk_high_threshold", "INTEGER")],
            "users": [("customer_id", "VARCHAR")],
            "interventions": [("owner", "VARCHAR"), ("status", "VARCHAR"), ("outcome", "TEXT"), ("follow_up_notes", "TEXT")],
        }
        for table, columns in additions.items():
            if table not in inspector.get_table_names():
                continue
            existing = {c["name"] for c in inspector.get_columns(table)}
            for column, sql_type in columns:
                if column not in existing:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))
        if "organizations" in inspector.get_table_names():
            connection.execute(text("UPDATE organizations SET risk_medium_threshold = 30 WHERE risk_medium_threshold IS NULL"))
            connection.execute(text("UPDATE organizations SET risk_high_threshold = 60 WHERE risk_high_threshold IS NULL"))

def _assign_existing_records(db, org_id: str):
    for model in (Customer, Agent, Case):
        db.query(model).filter(model.organization_id.is_(None)).update({model.organization_id: org_id}, synchronize_session=False)
    db.commit()

def _seed_demo_users(db, org_id: str):
    demo_case = db.query(Case).filter_by(case_id="CP-00006").first()
    demo_agent_id = demo_case.current_owner if demo_case else "Agent-01"
    demo_customer_id = demo_case.customer_id if demo_case else "CUS-00006"
    demo_users = [
        ("admin@carepulse.demo", "CarePulse Admin", "admin", None, None),
        ("cx.manager@carepulse.demo", "CX Manager", "cx_manager", None, None),
        ("business.manager@carepulse.demo", "Business Manager", "business_manager", None, None),
        ("agent@carepulse.demo", "Demo Agent", "agent", demo_agent_id, None),
        ("customer@carepulse.demo", "Demo Customer", "customer", None, demo_customer_id),
    ]
    for email, name, role, agent_id, customer_id in demo_users:
        existing = db.query(User).filter_by(email=email).first()
        if not existing:
            db.add(User(organization_id=org_id, email=email, display_name=name, role=role, agent_id=agent_id, customer_id=customer_id, password_hash=hash_password("carepulse-demo")))
        else:
            existing.organization_id = org_id
            existing.agent_id = agent_id
            existing.customer_id = customer_id
    db.commit()

def audit(db: Session, request: Request, action: str, resource: str, metadata: dict | None = None, org_id: str | None = None):
    user = getattr(request.state, "user", None)
    db.add(AuditLog(organization_id=org_id or organization_id(), user_id=user.user_id if user else None, action=action, resource=resource, metadata_json=json.dumps(metadata or {})))
    db.commit()

def safe_next(value: str) -> str:
    return value if value.startswith("/") and not value.startswith("//") else "/dashboard"

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

class ActionIn(BaseModel):
    action: str = Field(min_length=3, max_length=160)
    owner: str = Field(min_length=2, max_length=80)
    status: str = Field(default="planned", pattern="^(planned|in_progress|completed|cancelled)$")
    outcome: str = Field(default="", max_length=500)
    follow_up_notes: str = Field(default="", max_length=1000)

class ThresholdsIn(BaseModel):
    medium_threshold: int = Field(ge=1, le=99)
    high_threshold: int = Field(ge=2, le=100)

def load_case(db, case_id):
    query = db.query(Case).options(selectinload(Case.interactions), selectinload(Case.promises), selectinload(Case.interventions), selectinload(Case.feedback)).filter(Case.case_id == case_id)
    if organization_id():
        query = query.filter(Case.organization_id == organization_id())
    case = query.first()
    if not case:
        raise HTTPException(404, "Case not found")
    return case

def enforce_case_access(request: Request, case: Case):
    user = getattr(request.state, "user", None)
    if settings.app_env == "demo" or not user:
        return
    if user.role == "agent" and case.current_owner != user.agent_id:
        raise HTTPException(403, "You do not have permission to access this case.")
    if user.role == "customer" and case.customer_id != user.customer_id:
        raise HTTPException(403, "You do not have permission to access this case.")

def case_query(db):
    query = db.query(Case).options(selectinload(Case.interactions), selectinload(Case.promises), selectinload(Case.interventions), selectinload(Case.feedback))
    return query.filter(Case.organization_id == organization_id()) if organization_id() else query

def agent_query(db):
    query = db.query(Agent)
    return query.filter(Agent.organization_id == organization_id()) if organization_id() else query

@app.get("/health")
def health():
    return {"status": "ok", "service": "carepulse"}

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next: str = "/dashboard", error: str = ""):
    return templates.TemplateResponse(request, "login.html", {"request": request, "next": safe_next(next), "error": error, "demo_mode": settings.app_env == "demo"})

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...), password: str = Form(...), next: str = Form("/dashboard"), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email.strip().lower(), User.is_active.is_(True)).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "login.html", {"request": request, "next": safe_next(next), "error": "The email or password was not recognised. Please try again.", "demo_mode": settings.app_env == "demo"}, status_code=401)
    audit(db, request, "login", "session", {"role": user.role}, org_id=user.organization_id)
    response = RedirectResponse(safe_next(next), status_code=303)
    response.set_cookie(COOKIE_NAME, make_session(user.user_id), httponly=True, secure=settings.app_env == "production", samesite="lax", max_age=settings.session_ttl_hours * 3600)
    return response

@app.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    audit(db, request, "logout", "session")
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response

@app.get("/favicon.ico")
def favicon():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#ef8069"/><text x="32" y="42" text-anchor="middle" font-family="Arial" font-size="25" font-weight="700" fill="white">CP</text></svg>'
    return Response(svg, media_type="image/svg+xml")

@app.get("/api/cases")
def cases(request: Request, db: Session = Depends(get_db)):
    query = case_query(db)
    user = getattr(request.state, "user", None)
    if user and settings.app_env != "demo":
        if user.role == "agent":
            query = query.filter(Case.current_owner == user.agent_id)
        elif user.role == "customer":
            query = query.filter(Case.customer_id == user.customer_id)
    return [{"case_id": c.case_id, "industry": c.industry, "channel": c.channel, "issue_category": c.issue_category, "status": c.status} for c in query.limit(100).all()]

@app.get("/api/cases/{case_id}")
def case_detail(request: Request, case_id: str, db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    enforce_case_access(request, c)
    return {"case_id": c.case_id, "industry": c.industry, "channel": c.channel, "issue_category": c.issue_category, "priority": c.priority, "status": c.status, "silent_wait_minutes": silent_wait_minutes(c), "customer_effort": customer_effort(c), "risk": experience_risk(c), "recommendations": next_best_actions(c)}

@app.get("/api/cases/{case_id}/timeline")
def timeline(request: Request, case_id: str, db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    enforce_case_access(request, c)
    return [{"timestamp": i.timestamp, "actor": i.actor_type, "message": i.message, "sentiment": i.sentiment_ground_truth} for i in sorted(c.interactions, key=lambda x: x.timestamp)]

@app.get("/api/cases/{case_id}/risk")
def risk(request: Request, case_id: str, db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    enforce_case_access(request, c)
    return experience_risk(c)

@app.get("/api/cases/{case_id}/recommendation")
def recommendation(request: Request, case_id: str, db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    enforce_case_access(request, c)
    return {"actions": next_best_actions(c)}

@app.get("/api/metrics/overview")
def overview(db: Session = Depends(get_db)):
    cs = case_query(db).all()
    feedback = [c.feedback for c in cs if c.feedback]
    promises = [p for c in cs for p in c.promises]
    return {"total_cases": len(cs), "csat": round(sum(f.csat_score for f in feedback) / len(feedback), 2) if feedback else 0, "dsat_pct": round(sum(f.dsat_flag for f in feedback) / len(feedback) * 100, 1) if feedback else 0, "nps": round(sum((f.recommendation_score >= 9) - (f.recommendation_score <= 6) for f in feedback) / len(feedback) * 100, 1) if feedback else 0, "avg_first_response_min": round(sum(first_response_minutes(c) for c in cs) / len(cs), 1) if cs else 0, "avg_resolution_min": round(sum(resolution_minutes(c) for c in cs) / len(cs), 1) if cs else 0, "avg_silent_wait_min": round(sum(silent_wait_minutes(c) for c in cs) / len(cs), 1) if cs else 0, "promise_reliability": round(sum(p.promise_met for p in promises) / len(promises) * 100, 1) if promises else 0, "high_risk_cases": sum(experience_risk(c)["band"] == "HIGH" for c in cs)}

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
def create_event(request: Request, payload: EventIn, db: Session = Depends(get_db)):
    case = load_case(db, payload.case_id)
    enforce_case_access(request, case)
    try:
        event = ingest_event(db, case, payload.event_type, payload.event_timestamp or datetime.utcnow(), payload.actor_type, payload.message, payload.metadata, payload.actor_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    refreshed = load_case(db, payload.case_id)
    audit(db, request, "create_event", f"case:{payload.case_id}", {"event_type": payload.event_type})
    return {"event_id": event.event_id, "event_type": event.event_type, "case_id": event.case_id, "risk": experience_risk(refreshed), "recommendations": next_best_actions(refreshed)}

@app.post("/api/assistant")
def assistant_api(request: Request, payload: AssistantIn, db: Session = Depends(get_db)):
    case = load_case(db, payload.case_id) if payload.case_id else None
    if case:
        enforce_case_access(request, case)
    result = answer(payload.query, case=case, overview_data=overview(db) if case is None else None)
    audit(db, request, "assistant_query", f"case:{payload.case_id or 'overview'}")
    return result

@app.post("/api/cases/{case_id}/interactions")
def add_interaction(request: Request, case_id: str, message: str = Form(...), db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    enforce_case_access(request, c)
    user = getattr(request.state, "user", None)
    if user and settings.app_env != "demo" and user.role not in {"admin", "cx_manager", "business_manager", "agent"}:
        raise HTTPException(403, "Customers cannot record internal case updates.")
    result = classify(message)
    db.add(Interaction(interaction_id=f"MAN-{case_id}-{len(c.interactions)+1}", case_id=case_id, timestamp=datetime.utcnow(), interaction_type="message", actor_type="agent", message=message, sentiment_ground_truth=result["label"], sentiment_score=result["score"], meaningful_update_flag=True, transfer_flag=False, repeat_explanation_flag=False))
    db.commit()
    audit(db, request, "record_interaction", f"case:{case_id}")
    return RedirectResponse(f"/agent/{case_id}", status_code=303)

@app.post("/api/cases/{case_id}/actions")
def record_action(request: Request, case_id: str, payload: ActionIn, db: Session = Depends(get_db)):
    case = load_case(db, case_id)
    enforce_case_access(request, case)
    user = getattr(request.state, "user", None)
    if user and settings.app_env != "demo" and user.role not in {"admin", "cx_manager", "business_manager", "agent"}:
        raise HTTPException(403, "Customers cannot record internal actions.")
    now = datetime.utcnow()
    action = Intervention(
        intervention_id=f"ACT-{case_id}-{now.strftime('%Y%m%d%H%M%S%f')}",
        case_id=case.case_id,
        intervention_type=payload.action,
        intervention_at=now,
        reason="Recorded from agent workspace",
        accepted_flag=payload.status != "cancelled",
        owner=payload.owner,
        status=payload.status,
        outcome=payload.outcome or None,
        follow_up_notes=payload.follow_up_notes or None,
    )
    db.add(action)
    audit(db, request, "record_action", f"case:{case_id}", {"status": payload.status})
    return {"action_id": action.intervention_id, "status": action.status}

@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db)):
    org = db.get(Organization, organization_id())
    return templates.TemplateResponse(request, "settings.html", {"request": request, "organization": org, "saved": request.query_params.get("saved") == "1"})

@app.post("/api/settings/thresholds")
async def update_thresholds(request: Request, db: Session = Depends(get_db)):
    try:
        if "application/json" in request.headers.get("content-type", ""):
            payload = ThresholdsIn.model_validate(await request.json())
        else:
            payload = ThresholdsIn.model_validate(dict(await request.form()))
    except (ValidationError, ValueError, TypeError):
        raise HTTPException(422, "Provide valid medium and high risk thresholds.")
    if payload.medium_threshold >= payload.high_threshold:
        raise HTTPException(422, "The medium threshold must be lower than the high threshold.")
    org = db.get(Organization, organization_id())
    if not org:
        raise HTTPException(404, "Organisation not found")
    org.risk_medium_threshold = payload.medium_threshold
    org.risk_high_threshold = payload.high_threshold
    audit(db, request, "update_thresholds", f"organization:{org.organization_id}", {"medium": payload.medium_threshold, "high": payload.high_threshold})
    return RedirectResponse("/settings?saved=1", status_code=303)

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "home.html", {"request": request, "overview": overview(db)})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "dashboard.html", {"request": request, "overview": overview(db), "recovery": recovery(db), "drivers": drivers(db), "recs": recs(db)})

@app.get("/agent/{case_id}", response_class=HTMLResponse)
def agent(request: Request, case_id: str, db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    return templates.TemplateResponse(request, "agent.html", {"request": request, "case": c, "risk": experience_risk(c), "effort": customer_effort(c), "wait": silent_wait_minutes(c), "actions": next_best_actions(c)})

@app.get("/customer/{case_id}", response_class=HTMLResponse)
def customer_view(request: Request, case_id: str, db: Session = Depends(get_db)):
    c = load_case(db, case_id)
    return templates.TemplateResponse(request, "customer.html", {"request": request, "case": c, "wait": silent_wait_minutes(c)})

@app.get("/cases", response_class=HTMLResponse)
def case_list(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "cases.html", {"request": request, "cases": case_query(db).limit(30).all()})

def intelligence_context(db):
    cs = case_query(db).all()
    bands = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for c in cs:
        bands[experience_risk(c)["band"]] += 1
    return {"cases": cs, "bands": bands, "high_risk": sorted([c for c in cs if experience_risk(c)["band"] == "HIGH"], key=lambda c: experience_risk(c)["score"], reverse=True)[:12], "recovery": recovery_summary(cs), "overview": overview(db), "drivers": drivers(db), "recs": recs(db)}

@app.get("/story", response_class=HTMLResponse)
def story(request: Request, db: Session = Depends(get_db)):
    c = load_case(db, "CP-00006")
    return templates.TemplateResponse(request, "story.html", {"request": request, "case": c, "risk": experience_risk(c), "wait": silent_wait_minutes(c), "effort": customer_effort(c), "actions": next_best_actions(c), "recovery": recovery_summary([c])})

@app.get("/journey", response_class=HTMLResponse)
def journey(request: Request, db: Session = Depends(get_db)):
    c = load_case(db, "CP-00006")
    return templates.TemplateResponse(request, "journey.html", {"request": request, "case": c, "risk": experience_risk(c), "wait": silent_wait_minutes(c), "effort": customer_effort(c)})

@app.get("/risk-monitor", response_class=HTMLResponse)
def risk_monitor(request: Request, db: Session = Depends(get_db)):
    ctx = intelligence_context(db)
    return templates.TemplateResponse(request, "risk_monitor.html", {"request": request, "experience_risk": experience_risk, **ctx})

@app.get("/sentiment", response_class=HTMLResponse)
def sentiment_page(request: Request, db: Session = Depends(get_db)):
    c = load_case(db, "CP-00006")
    return templates.TemplateResponse(request, "sentiment.html", {"request": request, "case": c, "risk": experience_risk(c), "analysis": None})

@app.post("/sentiment/analyze", response_class=HTMLResponse)
def analyze_sentiment(request: Request, message: str = Form(...), source: str = Form("chat"), db: Session = Depends(get_db)):
    c = load_case(db, "CP-00006")
    return templates.TemplateResponse(request, "sentiment.html", {"request": request, "case": c, "risk": experience_risk(c), "analysis": classify(message, source), "input_message": message, "input_source": source})

@app.get("/promise-wait", response_class=HTMLResponse)
def promise_wait(request: Request, db: Session = Depends(get_db)):
    ctx = intelligence_context(db)
    promises = [p for c in ctx["cases"] for p in c.promises]
    return templates.TemplateResponse(request, "promise_wait.html", {"request": request, **ctx, "promises": promises})

@app.get("/dsat-drivers", response_class=HTMLResponse)
def dsat_drivers_page(request: Request, db: Session = Depends(get_db)):
    ctx = intelligence_context(db)
    return templates.TemplateResponse(request, "dsat_drivers.html", {"request": request, **ctx})

@app.get("/recovery", response_class=HTMLResponse)
def recovery_page(request: Request, db: Session = Depends(get_db)):
    ctx = intelligence_context(db)
    return templates.TemplateResponse(request, "recovery.html", {"request": request, **ctx})

@app.get("/recommendations", response_class=HTMLResponse)
def recommendations_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "recommendations.html", {"request": request, "recs": recs(db), "overview": overview(db)})

@app.get("/explorer", response_class=HTMLResponse)
def explorer(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "explorer.html", {"request": request, "cases": case_query(db).limit(40).all(), "table_name": "Cases", "purpose": "One row per customer journey, including context, ownership, timing, and status."})

@app.get("/insights", response_class=HTMLResponse)
def insights(request: Request, days: int = 90, industry: str = "", channel: str = "", issue: str = "", priority: str = "", agent: str = "", team: str = "", risk: str = "", sentiment: str = "", start: str = "", end: str = "", db: Session = Depends(get_db)):
    filters = Filters.from_query(days=days, industry=industry, channel=channel, issue=issue, priority=priority, agent=agent, team=team, risk=risk, sentiment=sentiment, start=start, end=end)
    all_cases = case_query(db).all()
    agents = agent_query(db).order_by(Agent.agent_id).all()
    filtered = apply_filters(all_cases, filters, agents)
    previous_filters = Filters.from_query(days=filters.days, industry=filters.industry, channel=filters.channel, issue=filters.issue, priority=filters.priority, agent=filters.agent, team=filters.team, risk=filters.risk, sentiment=filters.sentiment, start=(date.today() - timedelta(days=filters.days * 2)).isoformat(), end=(date.today() - timedelta(days=filters.days + 1)).isoformat())
    previous = apply_filters(all_cases, previous_filters, agents)
    return templates.TemplateResponse(request, "insights.html", {"request": request, "filters": filters, "filters_label": filters.label(), "metrics": metrics_for_cases(filtered), "comparison": comparison_metrics(filtered, previous), "history": monthly_rows(all_cases), "agents": agent_rows(filtered, agents), "teams": team_rows(filtered, agents), "recommendations": recommendations_for_cases(filtered), "agent_options": agents, "team_options": sorted({a.team for a in agents}), "industry_options": sorted({c.industry for c in all_cases}), "channel_options": sorted({c.channel for c in all_cases}), "issue_options": sorted({c.issue_category for c in all_cases}), "priority_options": sorted({c.priority for c in all_cases}), "risk_options": ["LOW", "MEDIUM", "HIGH"], "sentiment_options": ["positive", "neutral", "negative"]})

def filtered_report_cases(params, db):
    filters = Filters.from_query(**params)
    return apply_filters(case_query(db).all(), filters, agent_query(db).all()), filters

@app.get("/reports/cases.csv")
def report_csv(request: Request, db: Session = Depends(get_db)):
    cases, _ = filtered_report_cases(dict(request.query_params), db)
    return Response(csv_bytes(cases), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=carepulse-filtered-cases.csv"})

@app.get("/reports/analysis.xlsx")
def report_xlsx(request: Request, db: Session = Depends(get_db)):
    cases, _ = filtered_report_cases(dict(request.query_params), db)
    return Response(xlsx_bytes(cases), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=carepulse-analysis.xlsx"})

@app.get("/reports/executive.pdf")
def report_pdf(request: Request, db: Session = Depends(get_db)):
    cases, filters = filtered_report_cases(dict(request.query_params), db)
    return Response(pdf_bytes(cases, "CarePulse CX Report", filters.label()), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=carepulse-executive-report.pdf"})

@app.get("/reports/agent.pdf")
def agent_report_pdf(request: Request, db: Session = Depends(get_db)):
    cases, filters = filtered_report_cases(dict(request.query_params), db)
    return Response(pdf_bytes(cases, "CarePulse Agent CX Report", filters.label()), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=carepulse-agent-cx-report.pdf"})

@app.get("/reports/team.pdf")
def team_report_pdf(request: Request, db: Session = Depends(get_db)):
    cases, filters = filtered_report_cases(dict(request.query_params), db)
    return Response(pdf_bytes(cases, "CarePulse Team CX Report", filters.label()), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=carepulse-team-cx-report.pdf"})

@app.get("/methodology", response_class=HTMLResponse)
def methodology(request: Request):
    return templates.TemplateResponse(request, "methodology.html", {"request": request})

@app.get("/blueprint", response_class=HTMLResponse)
def blueprint(request: Request):
    return templates.TemplateResponse(request, "blueprint.html", {"request": request})

@app.get("/assistant", response_class=HTMLResponse)
def assistant_page(request: Request, query: str = Query(""), case_id: str = Query("CP-00006"), db: Session = Depends(get_db)):
    case = load_case(db, case_id) if case_id else None
    result = answer(query, case=case) if query.strip() else None
    return templates.TemplateResponse(request, "assistant.html", {"request": request, "result": result, "query": query, "case_id": case_id})

@app.post("/assistant", response_class=HTMLResponse)
def ask_assistant(request: Request, query: str = Form(...), case_id: str = Form("CP-00006"), db: Session = Depends(get_db)):
    case = load_case(db, case_id) if case_id else None
    return templates.TemplateResponse(request, "assistant.html", {"request": request, "result": answer(query, case=case), "query": query, "case_id": case_id})

@app.get("/simulator", response_class=HTMLResponse)
def simulator(request: Request, db: Session = Depends(get_db)):
    case = load_case(db, "CP-00006")
    return templates.TemplateResponse(request, "simulator.html", {"request": request, "case": case, "risk": experience_risk(case), "wait": silent_wait_minutes(case), "effort": customer_effort(case), "event_types": sorted(EVENT_TYPES), "notice": None})

@app.post("/simulator", response_class=HTMLResponse)
def simulator_emit(request: Request, event_type: str = Form(...), message: str = Form(""), db: Session = Depends(get_db)):
    case = load_case(db, "CP-00006")
    try:
        ingest_event(db, case, event_type, datetime.utcnow(), "customer" if "CUSTOMER" in event_type else "agent", message, {"channel": case.channel})
        notice = f"{event_type} ingested. Derived intelligence recalculated from the updated case."
    except ValueError as exc:
        notice = str(exc)
    case = load_case(db, "CP-00006")
    return templates.TemplateResponse(request, "simulator.html", {"request": request, "case": case, "risk": experience_risk(case), "wait": silent_wait_minutes(case), "effort": customer_effort(case), "event_types": sorted(EVENT_TYPES), "notice": notice})
