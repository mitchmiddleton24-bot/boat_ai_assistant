# src/api/weekly_reports.py

from fastapi import APIRouter
from src.services.weekly_summary_engine import generate_weekly_report

router = APIRouter()


@router.get("/weekly")
async def weekly_report():
    """
    Generate a real weekly report from uploaded files.
    """
    report_path = generate_weekly_report()
    return {
        "message": "Weekly report generated",
        "path": report_path,
    }
