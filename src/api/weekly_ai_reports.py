# src/api/weekly_ai_reports.py

from fastapi import APIRouter, HTTPException

from src.services.weekly_ai_engine import generate_weekly_ai_report


router = APIRouter(
    prefix="/weekly",
    tags=["Weekly AI Reports"],
)


@router.get("/auto-report")
def auto_report():
    """
    Automatically generates a full weekly AI report.
    Combines:
    - Email ingestion
    - GPT structured analysis
    - Claude executive report writing
    """
    try:
        result = generate_weekly_ai_report()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
