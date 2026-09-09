from pathlib import Path
import csv
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.database import SessionLocal
from src.models import Case
from src.metrics import customer_effort, silent_wait_minutes
from src.risk_engine import experience_risk

out = Path(__file__).resolve().parents[2] / "data" / "exports"
out.mkdir(parents=True, exist_ok=True)
db = SessionLocal()
cases = db.query(Case).all()
with (out / "cases_analysis.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["case_id","industry","channel","issue_category","priority","status","silent_wait_minutes","customer_effort","risk_band","risk_score","csat","dsat_flag"])
    for c in cases:
        r = experience_risk(c)
        writer.writerow([c.case_id,c.industry,c.channel,c.issue_category,c.priority,c.status,silent_wait_minutes(c),customer_effort(c),r["band"],r["score"],c.feedback.csat_score if c.feedback else "",c.feedback.dsat_flag if c.feedback else ""])
print(f"Exported {len(cases)} rows to {out / 'cases_analysis.csv'}")

