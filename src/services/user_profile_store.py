import json
from pathlib import Path
from typing import Optional, Dict
from src.models.user_profile import UserProfile

DATA_DIR = Path("src/data")
DATA_DIR.mkdir(exist_ok=True)

USER_FILE = DATA_DIR / "user_profiles.json"

def _load_all() -> Dict[str, dict]:
    if not USER_FILE.exists():
        return {}
    return json.loads(USER_FILE.read_text())

def _save_all(data: Dict[str, dict]) -> None:
    USER_FILE.write_text(json.dumps(data, indent=2))

def save_user_profile(profile: UserProfile) -> None:
    data = _load_all()
    data[profile.user_id] = profile.to_dict()
    _save_all(data)

def get_user_profile(user_id: str) -> Optional[UserProfile]:
    data = _load_all()
    if user_id not in data:
        return None
    return UserProfile.from_dict(data[user_id])

def get_user_by_email(email: str) -> Optional[UserProfile]:
    data = _load_all()
    for p in data.values():
        if p.get("email") == email:
            return UserProfile.from_dict(p)
    return None

def get_all_connected_users():
    data = _load_all()
    return [
        UserProfile.from_dict(p)
        for p in data.values()
        if p.get("outlook_connected")
    ]
