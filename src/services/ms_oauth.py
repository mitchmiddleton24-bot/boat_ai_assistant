# src/services/ms_oauth.py

from __future__ import annotations

import os
import urllib.parse
from typing import Dict, Any

import requests

MS_CLIENT_ID = os.getenv("MS_CLIENT_ID", "")
MS_TENANT_ID = os.getenv("MS_TENANT_ID", "common")
MS_CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET", "")
MS_REDIRECT_URI = os.getenv("MS_REDIRECT_URI", "")
MS_AUTHORITY = os.getenv("MS_AUTHORITY", f"https://login.microsoftonline.com/{MS_TENANT_ID}")

# Delegated scopes for per-user mailbox access
# Keep this string format because Microsoft expects a space-delimited string
MS_SCOPES = os.getenv("MS_SCOPES", "openid profile offline_access Mail.Read Mail.Send User.Read")


def build_authorize_url(state: str) -> str:
    params = {
        "client_id": MS_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": MS_REDIRECT_URI,
        "response_mode": "query",
        "scope": MS_SCOPES,
        "state": state,
    }
    return f"{MS_AUTHORITY}/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"


def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
    token_url = f"{MS_AUTHORITY}/oauth2/v2.0/token"
    data = {
        "client_id": MS_CLIENT_ID,
        "client_secret": MS_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": MS_REDIRECT_URI,
        "scope": MS_SCOPES,
    }
    resp = requests.post(token_url, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    token_url = f"{MS_AUTHORITY}/oauth2/v2.0/token"
    data = {
        "client_id": MS_CLIENT_ID,
        "client_secret": MS_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": MS_REDIRECT_URI,
        "scope": MS_SCOPES,
    }
    resp = requests.post(token_url, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()
