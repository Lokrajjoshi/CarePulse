from io import BytesIO
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from src.analytics import metrics_for_cases, recommendations_for_cases


def _case_rows(cases):
    return [{"case_id": c.case_id, "agent": c.current_owner, "industry": c.industry, "channel": c.channel, "issue": c.issue_category, "priority": c.priority, "status": c.status, "csat": c.feedback.csat_score if c.feedback else None, "dsat": bool(c.feedback and c.feedback.dsat_flag)} for c in cases]


def csv_bytes(cases):
    return pd.DataFrame(_case_rows(cases)).to_csv(index=False).encode("utf-8")


def xlsx_bytes(cases):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame([metrics_for_cases(cases)]).to_excel(writer, index=False, sheet_name="Executive Summary")
        pd.DataFrame(_case_rows(cases)).to_excel(writer, index=False, sheet_name="Cases")
        pd.DataFrame(recommendations_for_cases(cases)).to_excel(writer, index=False, sheet_name="Recommendations")
    return output.getvalue()


def pdf_bytes(cases, title, filters_label):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    metrics = metrics_for_cases(cases)
    story = [Paragraph(title, styles["Title"]), Paragraph("Operational Coaching & CX Insight" if "Agent" in title else "CarePulse CX Report", styles["Heading2"]), Spacer(1, 8), Paragraph(f"Filters applied: {filters_label}<br/>Synthetic demonstration data.", styles["BodyText"]), Spacer(1, 14)]
    rows = [["KPI", "Value"], ["Total cases", metrics["cases"]], ["CSAT", metrics["csat"]], ["DSAT", f'{metrics["dsat_pct"]}%'], ["NPS", metrics["nps"]], ["Silent Wait", f'{metrics["silent_wait"]} min'], ["Promise Reliability", f'{metrics["promise_reliability"]}%'], ["Repeat Contact", f'{metrics["repeat_contact"]}%'], ["Recovery Rate", f'{metrics["recovery_rate"]}%']]
    table = Table(rows, colWidths=[220, 150])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d766f")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#ccd9d8")), ("PADDING", (0, 0), (-1, -1), 7)]))
    story.append(table)
    story += [Spacer(1, 14), Paragraph("Top business observations", styles["Heading2"])]
    for item in recommendations_for_cases(cases):
        story += [Paragraph(f'<b>{item["observation"]}</b><br/>Evidence: {item["evidence"]}<br/>Potential impact: {item["impact"]}<br/>Recommended action: {item["action"]}<br/>Measure: {item["measure"]}', styles["BodyText"]), Spacer(1, 8)]
    story.append(Paragraph("Observed associations do not automatically establish causation. Use this report for investigation and service improvement, not employee punishment.", styles["BodyText"]))
    doc.build(story)
    return output.getvalue()
