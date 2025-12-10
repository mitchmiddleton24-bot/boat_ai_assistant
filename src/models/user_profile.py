# src/models/user_profile.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class UserProfile:
    id: str                       # internal id, like "mitch" or a uuid
    primary_email: str            # the Outlook email you read from
    report_recipients: List[str] = field(default_factory=list)

    # Intelligence settings
    follow_up_threshold_hours: int = 48
    stale_info_days: int = 7
    ignore_domains: List[str] = field(default_factory=list)
    subcontractor_domains: List[str] = field(default_factory=list)

    # Future flags
    is_active: bool = True
