from fastapi import APIRouter
from services.report_engine import load_latest_reports

router = APIRouter()

@router.get("/weekly")
def get_weekly_report():
    return {"report": load_latest_reports()}
