# src/models/user_profile.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class UserProfile:
    # Core identity
    user_id: str
    email: str
    display_name: str
    tenant_id: str

    # Multi-tenant / org routing (optional)
    org_id: Optional[str] = None

    # Connection state
    outlook_connected: bool = False
    outlook_tokens: Dict[str, Any] = field(default_factory=dict)

    # Report behavior defaults
    follow_up_threshold_hours: int = 24
    stale_info_days: int = 7

    # Metadata
    created_at: str = field(default_factory=_utc_now_iso)

    # Compatibility helpers (older code expects these names)
    @property
    def id(self) -> str:
        return self.user_id

    @property
    def primary_email(self) -> str:
        return self.email

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "display_name": self.display_name,
            "tenant_id": self.tenant_id,
            "org_id": self.org_id,
            "outlook_connected": self.outlook_connected,
            "outlook_tokens": self.outlook_tokens,
            "follow_up_threshold_hours": self.follow_up_threshold_hours,
            "stale_info_days": self.stale_info_days,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UserProfile":
        return UserProfile(
            user_id=data.get("user_id", ""),
            email=data.get("email", ""),
            display_name=data.get("display_name", ""),
            tenant_id=data.get("tenant_id", ""),
            org_id=data.get("org_id"),
            outlook_connected=bool(data.get("outlook_connected", False)),
            outlook_tokens=data.get("outlook_tokens") or {},
            follow_up_threshold_hours=int(data.get("follow_up_threshold_hours", 24)),
            stale_info_days=int(data.get("stale_info_days", 7)),
            created_at=data.get("created_at") or _utc_now_iso(),
        )
