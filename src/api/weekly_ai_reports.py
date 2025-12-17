# src/api/weekly_ai_reports.py

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from src.services.weekly_ai_engine import (
    generate_weekly_ai_report,
    generate_and_email_weekly_report,
)
from src.services.user_profile_store import get_all_connected_users

router = APIRouter(prefix="/weekly", tags=["Weekly AI Reports"])


class ReportRequest(BaseModel):
    user_id: Optional[str] = None


class EmailReportRequest(BaseModel):
    to_addresses: List[str]
    user_id: Optional[str] = None


@router.get("/connected-users")
def connected_users():
    try:
        users = get_all_connected_users()
        return [
            {
                "user_id": u.user_id,
                "email": u.email,
                "display_name": u.display_name,
                "tenant_id": u.tenant_id,
            }
            for u in users
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/report")
def generate_report(payload: ReportRequest):
    try:
        return generate_weekly_ai_report(user_id=payload.user_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/email-report")
def email_report(payload: EmailReportRequest):
    try:
        return generate_and_email_weekly_report(
            to_addresses=payload.to_addresses,
            user_id=payload.user_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
