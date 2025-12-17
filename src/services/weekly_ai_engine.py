# src/services/weekly_ai_engine.py

from __future__ import annotations

from datetime import datetime, timedelta
import os
from typing import List, Dict, Any, Optional

from openai import OpenAI
import anthropic

from src.models.user_profile import UserProfile
from src.services.user_profile_store import (
    get_all_connected_users,
    get_user_profile_by_id,
)
from src.services.ms_graph_client import (
    get_recent_inbox_and_sent_emails,
    send_email,
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


def _pick_profile(user_id: Optional[str]) -> UserProfile:
    if user_id:
        p = get_user_profile_by_id(user_id)
        if not p:
            raise RuntimeError(f"No user profile found for user_id={user_id}")
        if not p.outlook_connected:
            raise RuntimeError(f"User {user_id} exists but is not Outlook-connected")
        return p

    users = get_all_connected_users()
    if not users:
        raise RuntimeError("No Outlook-connected users found. Connect an account first.")
    return users[0]


def _get_delegated_access_token(profile: UserProfile) -> Optional[str]:
    tokens = profile.outlook_tokens or {}
    return tokens.get("access_token")


def fetch_emails_last_7_days(access_token: Optional[str]) -> List[Dict[str, Any]]:
    now_utc = datetime.utcnow()
    cutoff = now_utc - timedelta(days=7)

    raw_emails = get_recent_inbox_and_sent_emails(top=200, access_token=access_token)
    filtered: List[Dict[str, Any]] = []

    for msg in raw_emails:
        dt_str = msg.get("receivedDateTime") or msg.get("sentDateTime")
        if not dt_str:
            continue

        cleaned = dt_str.replace("Z", "")
        try:
            msg_dt = datetime.fromisoformat(cleaned)
        except Exception:
            continue

        if msg_dt >= cutoff:
            filtered.append(msg)

    return filtered


def group_emails_into_conversations(emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    conv_map: Dict[str, List[Dict[str, Any]]] = {}
    for msg in emails:
        conv_id = msg.get("conversationId") or "no-conversation-id"
        conv_map.setdefault(conv_id, []).append(msg)

    conversations: List[Dict[str, Any]] = []

    for conv_id, msgs in conv_map.items():
        def sort_key(m: Dict[str, Any]) -> str:
            return m.get("sentDateTime") or m.get("receivedDateTime") or ""

        msgs_sorted = sorted(msgs, key=sort_key)
        conversations.append(
            {
                "conversation_id": conv_id,
                "messages": msgs_sorted,
                "count": len(msgs_sorted),
            }
        )

    conversations.sort(key=lambda c: c["count"], reverse=True)
    return conversations


def _format_prompt(profile: UserProfile, conversations: List[Dict[str, Any]]) -> str:
    # Keep it simple and deterministic. You can expand later.
    lines: List[str] = []
    lines.append(f"Generate a weekly executive summary for: {profile.display_name} ({profile.email})")
    lines.append("Use plain text, short sections, and be direct.")
    lines.append("")
    lines.append(f"Total conversations: {len(conversations)}")
    lines.append("")

    for i, conv in enumerate(conversations[:25], start=1):
        lines.append(f"Conversation {i} (messages={conv['count']}):")
        for m in conv["messages"][-5:]:
            subj = m.get("subject", "")
            prev = m.get("bodyPreview", "")
            frm = (m.get("from") or {}).get("emailAddress", {}).get("address", "")
            lines.append(f"- From: {frm} | Subject: {subj} | Preview: {prev}")
        lines.append("")

    lines.append("Output sections:")
    lines.append("1) Key Wins")
    lines.append("2) Risks and Blind Spots")
    lines.append("3) Follow Ups Needed")
    lines.append("4) Suggested Next Actions")
    return "\n".join(lines)


def _call_claude(prompt: str) -> str:
    if not CLAUDE_API_KEY:
        raise RuntimeError("Missing CLAUDE_API_KEY")

    resp = claude_client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest"),
        max_tokens=1400,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def generate_weekly_ai_report(user_id: str | None = None) -> Dict[str, Any]:
    profile = _pick_profile(user_id)
    access_token = _get_delegated_access_token(profile)

    emails = fetch_emails_last_7_days(access_token=access_token)
    conversations = group_emails_into_conversations(emails)

    prompt = _format_prompt(profile, conversations)
    report_text = _call_claude(prompt)

    return {
        "user_id": profile.user_id,
        "email": profile.email,
        "display_name": profile.display_name,
        "generated_at": datetime.utcnow().isoformat(),
        "conversation_count": len(conversations),
        "report_text": report_text,
    }


def generate_and_email_weekly_report(
    to_addresses: List[str],
    user_id: str | None = None,
) -> Dict[str, Any]:
    profile = _pick_profile(user_id)
    access_token = _get_delegated_access_token(profile)

    report = generate_weekly_ai_report(user_id=profile.user_id)

    subject = f"Weekly AI Report - {profile.display_name}"
    body = report["report_text"]

    send_email(
        subject=subject,
        body_text=body,
        to_addresses=to_addresses,
        access_token=access_token,
    )

    return {
        "ok": True,
        "sent_to": to_addresses,
        "report_user": {"user_id": profile.user_id, "email": profile.email},
    }
