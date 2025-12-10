# src/services/user_profile_store.py
import os
from typing import List, Optional
from src.models.user_profile import UserProfile

def get_default_user_profile() -> UserProfile:
    email = os.getenv("REPORT_USER_EMAIL") or os.getenv("MS_GRAPH_USER_ID") or ""
    recipients_env = os.getenv("REPORT_RECIPIENTS", "")
    recipients = [r.strip() for r in recipients_env.split(",") if r.strip()] or [email]

    return UserProfile(
        id="mitch",
        primary_email=email,
        report_recipients=recipients,
        follow_up_threshold_hours=48,
        stale_info_days=7,
        ignore_domains=[
            "microsoft.com",
            "relayfi.com",
            "zoom.us",
        ],
        subcontractor_domains=[
            # fill in later for real companies
        ],
    )

def get_all_user_profiles() -> List[UserProfile]:
    # For now, just you. Later this will read from a DB.
    return [get_default_user_profile()]

def get_user_profile_by_id(user_id: str) -> Optional[UserProfile]:
    for profile in get_all_user_profiles():
        if profile.id == user_id:
            return profile
    return None
