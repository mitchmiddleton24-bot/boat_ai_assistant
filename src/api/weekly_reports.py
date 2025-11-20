# src/api/weekly_reports.py

from fastapi import APIRouter
from src.services.report_generator import generate_weekly_report

router = APIRouter()

@router.get("/weekly", tags=["Reports"])
def weekly_report():
    return generate_weekly_report()
