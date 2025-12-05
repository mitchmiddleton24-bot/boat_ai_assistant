# src/api/weekly_ai_reports.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.weekly_ai_engine import (
    generate_weekly_ai_report,
    generate_and_email_weekly_report,
)


router = APIRouter(
    prefix="/weekly",
    tags=["Weekly AI Reports"],
)


class EmailReportRequest(BaseModel):
    to_addresses: list[str]


@router.get("/auto-report")
def auto_report():
    """
    Generate a weekly AI report and return it in the response.
    """
    try:
        result = generate_weekly_ai_report()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/email-report")
def email_report(payload: EmailReportRequest):
    """
    Generate a weekly AI report and email it to the provided addresses.
    This is the endpoint that a scheduler will call automatically.
    """
    try:
        result = generate_and_email_weekly_report(payload.to_addresses)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
