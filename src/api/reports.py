from fastapi import APIRouter
from src.services.report_engine import generate_dummy_weekly_report

router = APIRouter()

@router.get("/weekly")
async def get_weekly_report():
    """Returns a dummy weekly report."""
    file_path = generate_dummy_weekly_report()
    return {"detail": "Weekly report created", "path": file_path}
