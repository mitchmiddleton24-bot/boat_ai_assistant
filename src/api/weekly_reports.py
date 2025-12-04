from fastapi import APIRouter
from src.services.report_engine import generate_dummy_weekly_report

router = APIRouter()

@router.get("/weekly")
async def weekly_report():
    """
    Temporary endpoint for a weekly report.

    Right now this just calls a dummy generator that writes a text file
    into src/data/reports and returns the path. Later we will swap this
    for a real Outlook plus Otter plus AI summary.
    """
    report_path = generate_dummy_weekly_report()

    return {
        "message": "Weekly report generated",
        "path": report_path,
    }