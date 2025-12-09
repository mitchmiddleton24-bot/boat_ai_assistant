# src/services/ms_graph_client.py

import os
from typing import List, Dict, Any

import msal
import requests

TENANT_ID = os.getenv("MS_TENANT_ID")
CLIENT_ID = os.getenv("MS_CLIENT_ID")
CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET")
USER_ID = os.getenv("MS_GRAPH_USER_ID")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_URL = "https://graph.microsoft.com/v1.0"


def _get_access_token() -> str:
    """
    Get an application level access token using client credentials.
    Uses the MS_* environment variables.
    """
    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        raise RuntimeError("Missing one or more MS_* environment variables")

    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

    result = app.acquire_token_silent(SCOPE, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=SCOPE)

    if "access_token" not in result:
        raise RuntimeError(f"Could not acquire token from MSAL: {result}")

    return result["access_token"]


def get_recent_emails(top: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch recent emails from the configured user's mailbox.
    Returns a simplified list with subject, from, and received time.
    """
    if not USER_ID:
        raise RuntimeError("MS_GRAPH_USER_ID is not set")

    token = _get_access_token()

    url = (
        f"{GRAPH_URL}/users/{USER_ID}/messages"
        f"?$top={top}&$orderby=receivedDateTime desc"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(
            f"Graph API error {response.status_code}: {response.text}"
        )

    items = response.json().get("value", [])

    simplified: List[Dict[str, Any]] = []
    for item in items:
        simplified.append(
            {
                "id": item.get("id"),
                "subject": item.get("subject"),
                "from": (item.get("from") or {})
                .get("emailAddress", {})
                .get("address"),
                "receivedDateTime": item.get("receivedDateTime"),
            }
        )

    return simplified

from typing import List, Dict, Any  # you probably already have this at the top

def get_recent_inbox_and_sent_emails(top: int = 200) -> List[Dict[str, Any]]:
    """
    Fetch recent emails from both Inbox and Sent Items for the configured user.
    Returns a combined list with basic thread information.
    """
    if not USER_ID:
        raise RuntimeError("MS_GRAPH_USER_ID is not set")

    token = _get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    all_messages: List[Dict[str, Any]] = []

    # Inbox
    inbox_url = (
        f"{GRAPH_URL}/users/{USER_ID}/mailFolders('Inbox')/messages"
        f"?$top={top}&$orderby=receivedDateTime desc"
    )
    inbox_resp = requests.get(inbox_url, headers=headers, timeout=30)
    if inbox_resp.status_code != 200:
        raise RuntimeError(
            f"Graph Inbox error {inbox_resp.status_code}: {inbox_resp.text}"
        )
    inbox_items = inbox_resp.json().get("value", [])

    for item in inbox_items:
        all_messages.append(
            {
                "id": item.get("id"),
                "subject": item.get("subject"),
                "from": (item.get("from") or {})
                .get("emailAddress", {})
                .get("address"),
                "to": [
                    (recip.get("emailAddress") or {}).get("address")
                    for recip in item.get("toRecipients", [])
                ],
                "receivedDateTime": item.get("receivedDateTime"),
                "sentDateTime": item.get("sentDateTime"),
                "conversationId": item.get("conversationId"),
                "bodyPreview": item.get("bodyPreview"),
                "folder": "inbox",
            }
        )

    # Sent Items
    sent_url = (
        f"{GRAPH_URL}/users/{USER_ID}/mailFolders('SentItems')/messages"
        f"?$top={top}&$orderby=sentDateTime desc"
    )
    sent_resp = requests.get(sent_url, headers=headers, timeout=30)
    if sent_resp.status_code != 200:
        raise RuntimeError(
            f"Graph SentItems error {sent_resp.status_code}: {sent_resp.text}"
        )
    sent_items = sent_resp.json().get("value", [])

    for item in sent_items:
        all_messages.append(
            {
                "id": item.get("id"),
                "subject": item.get("subject"),
                "from": (item.get("from") or {})
                .get("emailAddress", {})
                .get("address"),
                "to": [
                    (recip.get("emailAddress") or {}).get("address")
                    for recip in item.get("toRecipients", [])
                ],
                "receivedDateTime": item.get("receivedDateTime"),
                "sentDateTime": item.get("sentDateTime"),
                "conversationId": item.get("conversationId"),
                "bodyPreview": item.get("bodyPreview"),
                "folder": "sent",
            }
        )

    return all_messages

def send_email(subject: str, body_text: str, to_addresses: list[str]) -> None:
    """
    Send an email using Microsoft Graph from the configured user.
    Uses application permissions and MS_* environment variables.
    """
    if not USER_ID:
        raise RuntimeError("MS_GRAPH_USER_ID is not set")

    token = _get_access_token()

    url = f"{GRAPH_URL}/users/{USER_ID}/sendMail"

    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body_text,
            },
            "toRecipients": [
                {"emailAddress": {"address": addr}} for addr in to_addresses
            ],
        },
        "saveToSentItems": True,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=message, timeout=30)

    if response.status_code not in (202, 200):
        raise RuntimeError(
            f"Graph sendMail error {response.status_code}: {response.text}"
        )
