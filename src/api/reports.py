from fastapi import APIRouter
from src.services.report_generator import generate_weekly_report

router = APIRouter()

@router.get("/weekly")
async def get_weekly_report():
    """
    Generate a dummy weekly report.
    Replace with real logic later.
    """
    report = await generate_weekly_report()
    return {"weekly_report": report}
