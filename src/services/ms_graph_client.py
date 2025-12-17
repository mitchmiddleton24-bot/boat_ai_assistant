# src/services/ms_graph_client.py

from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

import msal
import requests

TENANT_ID = os.getenv("MS_TENANT_ID")
CLIENT_ID = os.getenv("MS_CLIENT_ID")
CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET")

# App-only fallback user (your older single-mailbox setup)
APP_ONLY_USER_ID = os.getenv("MS_GRAPH_USER_ID")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}" if TENANT_ID else ""
SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_URL = "https://graph.microsoft.com/v1.0"


def _get_app_only_access_token() -> str:
    """
    Application level access token using client credentials (older mode).
    """
    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        raise RuntimeError("Missing one or more MS_* environment variables for app-only token")

    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" not in result:
        raise RuntimeError(f"Failed to acquire app token: {result}")
    return result["access_token"]


def _graph_get(url: str, access_token: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _graph_post(url: str, access_token: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=json_body, timeout=30)
    if resp.status_code >= 400:
        raise RuntimeError(f"Graph POST failed ({resp.status_code}): {resp.text}")
    return resp.json() if resp.text else {"ok": True}


def get_me(access_token: str) -> Dict[str, Any]:
    return _graph_get(f"{GRAPH_URL}/me", access_token)


def get_recent_inbox_and_sent_emails(
    top: int = 200,
    access_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    If access_token is provided, uses delegated /me access (multi-user SaaS).
    Otherwise falls back to app-only mode using /users/{APP_ONLY_USER_ID}.
    """
    if access_token:
        base = f"{GRAPH_URL}/me"
        token = access_token
    else:
        if not APP_ONLY_USER_ID:
            raise RuntimeError("MS_GRAPH_USER_ID not set and no delegated access_token provided")
        base = f"{GRAPH_URL}/users/{APP_ONLY_USER_ID}"
        token = _get_app_only_access_token()

    # Pull from Inbox and SentItems
    inbox_url = (
        f"{base}/mailFolders/Inbox/messages"
        f"?$top={top}&$orderby=receivedDateTime desc"
        f"&$select=subject,bodyPreview,from,toRecipients,ccRecipients,receivedDateTime,sentDateTime,conversationId,id"
    )
    sent_url = (
        f"{base}/mailFolders/SentItems/messages"
        f"?$top={top}&$orderby=sentDateTime desc"
        f"&$select=subject,bodyPreview,from,toRecipients,ccRecipients,receivedDateTime,sentDateTime,conversationId,id"
    )

    inbox = _graph_get(inbox_url, token).get("value", [])
    sent = _graph_get(sent_url, token).get("value", [])
    return inbox + sent


def send_email(
    subject: str,
    body_text: str,
    to_addresses: List[str],
    access_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    If access_token is provided, sends from /me (multi-user).
    Otherwise sends from the app-only user mailbox (older mode).
    """
    if access_token:
        url = f"{GRAPH_URL}/me/sendMail"
        token = access_token
    else:
        if not APP_ONLY_USER_ID:
            raise RuntimeError("MS_GRAPH_USER_ID not set and no delegated access_token provided")
        url = f"{GRAPH_URL}/users/{APP_ONLY_USER_ID}/sendMail"
        token = _get_app_only_access_token()

    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body_text},
            "toRecipients": [{"emailAddress": {"address": a}} for a in to_addresses],
        },
        "saveToSentItems": True,
    }
    return _graph_post(url, token, payload)
