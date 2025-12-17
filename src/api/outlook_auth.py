# src/api/outlook_auth.py

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
import secrets
import base64
import json

import requests

from src.services.ms_oauth import build_authorize_url, exchange_code_for_tokens
from src.services.user_profile_store import (
    get_user_by_email,
    save_user_profile,
)
from src.models.user_profile import UserProfile

router = APIRouter(prefix="/auth/outlook", tags=["Outlook OAuth"])

# For production SaaS this must be per session/user.
OAUTH_STATE = secrets.token_urlsafe(16)


def _jwt_payload(token: str) -> dict:
    """
    Decode JWT payload without verifying signature.
    Enough to extract tid/oid in a controlled app environment.
    """
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload_b64 = parts[1]
        pad = "=" * (-len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + pad)
        return json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return {}


def _graph_me(access_token: str) -> dict:
    resp = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )
    if resp.status_code >= 400:
        raise HTTPException(status_code=400, detail=f"Graph /me failed: {resp.text}")
    return resp.json()


@router.get("/login")
def outlook_login():
    auth_url = build_authorize_url(OAUTH_STATE)
    return RedirectResponse(url=auth_url)


@router.get("/callback")
def outlook_callback(code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code' in callback")
    if state != OAUTH_STATE:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    token_data = exchange_code_for_tokens(code)
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="No access_token returned by Microsoft")

    me = _graph_me(access_token)

    # Email can be null in some tenants, fall back to UPN
    email = (me.get("mail") or me.get("userPrincipalName") or "").strip()
    display_name = (me.get("displayName") or email or "Connected User").strip()
    graph_user_id = (me.get("id") or "").strip()

    claims = _jwt_payload(access_token)
    tenant_id = (claims.get("tid") or "").strip()
    oid = (claims.get("oid") or "").strip()

    # Prefer stable IDs
    user_id = graph_user_id or oid or email
    if not user_id or not email:
        raise HTTPException(status_code=400, detail="Unable to determine user identity from Graph /me")

    existing = get_user_by_email(email)
    if existing:
        profile = existing
        profile.display_name = display_name
        profile.tenant_id = tenant_id or existing.tenant_id
    else:
        profile = UserProfile(
            user_id=user_id,
            email=email,
            display_name=display_name,
            tenant_id=tenant_id or "unknown",
        )

    profile.outlook_connected = True
    profile.outlook_tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "scope": token_data.get("scope"),
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type"),
    }

    save_user_profile(profile)

    # Simple human-friendly confirmation page
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>Outlook Connected</h2>
        <p><b>User:</b> {profile.display_name}</p>
        <p><b>Email:</b> {profile.email}</p>
        <p>You can close this tab.</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
