# src/api/outlook_auth.py

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
import secrets
import requests

from src.services.ms_oauth import build_authorize_url, exchange_code_for_tokens
from src.services.user_profile_store import save_user_profile, get_user_profile
from src.models.user_profile import UserProfile

router = APIRouter(prefix="/auth/outlook", tags=["Outlook OAuth"])

# NOTE: For real multi-user SaaS, "state" must be per-user/session.
# This static state is OK only for your current testing.
OAUTH_STATE = secrets.token_urlsafe(16)


def _get_me(access_token: str) -> dict:
    """
    Fetch basic user identity from Microsoft Graph using the delegated token.
    Requires User.Read (you already added it).
    """
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
    """
    Redirect the user to Microsoft login to connect their Outlook inbox.
    """
    auth_url = build_authorize_url(OAUTH_STATE)
    return RedirectResponse(url=auth_url)


@router.get("/callback")
def outlook_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    """
    OAuth callback endpoint. Microsoft redirects here after login.
    Saves tokens into the user's profile store.
    """
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
        raise HTTPException(status_code=400, detail="No access_token returned from token exchange")

    # Identify who just connected (email + id)
    me = _get_me(access_token)
    ms_user_id = me.get("id") or "unknown-ms-id"
    email = me.get("mail") or me.get("userPrincipalName") or "unknown-email"
    display_name = me.get("displayName") or email

    # Load existing profile or create new
    existing = get_user_profile(ms_user_id)
    if existing:
        profile = existing
        profile.email = email
        profile.display_name = display_name
        profile.outlook_connected = True
        profile.outlook_tokens = {
            "token_type": token_data.get("token_type"),
            "scope": token_data.get("scope"),
            "expires_in": token_data.get("expires_in"),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    else:
        profile = UserProfile(
            user_id=ms_user_id,
            email=email,
            display_name=display_name,
            tenant_id="ms-oauth",  # placeholder for now
            org_id=None,
            outlook_connected=True,
            outlook_tokens={
                "token_type": token_data.get("token_type"),
                "scope": token_data.get("scope"),
                "expires_in": token_data.get("expires_in"),
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        )

    save_user_profile(profile)

    # Return a simple confirmation that is safe to show in a browser
    return JSONResponse(
        {
            "message": "Outlook account connected",
            "user_id": profile.user_id,
            "email": profile.email,
            "display_name": profile.display_name,
            "scope": token_data.get("scope"),
            "expires_in": token_data.get("expires_in"),
            "stored_tokens": True,
        }
    )
