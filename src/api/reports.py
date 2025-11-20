# src/api/reports.py

from fastapi import APIRouter
from services.reports.weekly_report import generate_weekly_report

router = APIRouter()

@router.get("/weekly")
async def weekly_report():
    report = generate_weekly_report()
    return {"weekly_report": report}
