# src/api/outlook_auth.py

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
import secrets

from src.services.ms_oauth import build_authorize_url, exchange_code_for_tokens

router = APIRouter(prefix="/auth/outlook", tags=["Outlook OAuth"])

# In a real app you would store state per user; for now, a simple static state is OK for testing.
OAUTH_STATE = secrets.token_urlsafe(16)


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
    For now we just return token previews so you can confirm it works.
    """
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code' in callback")
    if state != OAUTH_STATE:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    token_data = exchange_code_for_tokens(code)

    # In a later step, we will save these tokens to a UserProfile in a database.
    return JSONResponse(
        {
            "message": "Outlook account connected (test mode)",
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "scope": token_data.get("scope"),
            "access_token_preview": (token_data.get("access_token") or "")[:40] + "...",
            "refresh_token_preview": (token_data.get("refresh_token") or "")[:40] + "...",
        }
    )
