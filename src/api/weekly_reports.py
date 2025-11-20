from fastapi import APIRouter
from src.services.report_engine import generate_dummy_weekly_report

router = APIRouter()

@router.get("/weekly")
async def weekly_report():
    """
    Returns a dummy weekly report.
    Later you will replace this with real executive-level summaries.
    """
    report_path = generate_dummy_weekly_report()
    return {
        "message": "Weekly report generated",
        "path": report_path
    }
