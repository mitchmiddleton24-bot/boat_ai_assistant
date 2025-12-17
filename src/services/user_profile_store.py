# src/services/user_profile_store.py

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional, Dict, List

from src.models.user_profile import UserProfile

DATA_DIR = Path("src/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

USER_FILE = DATA_DIR / "user_profiles.json"


def _load_all() -> Dict[str, dict]:
    if not USER_FILE.exists():
        return {}
    raw = USER_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    return json.loads(raw)


def _save_all(data: Dict[str, dict]) -> None:
    USER_FILE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def save_user_profile(profile: UserProfile) -> None:
    data = _load_all()
    data[profile.user_id] = profile.to_dict()
    _save_all(data)


def get_user_profile(user_id: str) -> Optional[UserProfile]:
    data = _load_all()
    p = data.get(user_id)
    return UserProfile.from_dict(p) if p else None


# Backward compatible alias (some files import this name)
def get_user_profile_by_id(user_id: str) -> Optional[UserProfile]:
    return get_user_profile(user_id)


def get_user_by_email(email: str) -> Optional[UserProfile]:
    email_norm = (email or "").strip().lower()
    if not email_norm:
        return None

    data = _load_all()
    for p in data.values():
        if (p.get("email") or "").strip().lower() == email_norm:
            return UserProfile.from_dict(p)
    return None


def get_all_connected_users() -> List[UserProfile]:
    data = _load_all()
    users: List[UserProfile] = []
    for p in data.values():
        if p.get("outlook_connected"):
            users.append(UserProfile.from_dict(p))
    return users


def upsert_user_by_email(profile: UserProfile) -> UserProfile:
    """
    If a user with this email exists, overwrite that record with the new profile
    but keep the existing user_id if the new one is empty.
    """
    existing = get_user_by_email(profile.email)
    if existing:
        if not profile.user_id:
            profile.user_id = existing.user_id
    save_user_profile(profile)
    return profile


def get_default_user_profile() -> Optional[UserProfile]:
    """
    Backward compatible helper.
    Option B removes its usage in weekly_ai_engine, but other modules may still call it.
    Preference order:
      1) REPORT_USER_EMAIL env match
      2) first connected user
      3) None
    """
    env_email = (os.getenv("REPORT_USER_EMAIL") or "").strip().lower()
    if env_email:
        found = get_user_by_email(env_email)
        if found:
            return found

    users = get_all_connected_users()
    return users[0] if users else None
