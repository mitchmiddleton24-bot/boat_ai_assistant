# src/services/ms_oauth.py

import os
import urllib.parse
from typing import Dict, Any

import requests

MS_CLIENT_ID = os.getenv("MS_CLIENT_ID", "")
MS_TENANT_ID = os.getenv("MS_TENANT_ID", "common")
MS_CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET", "")
MS_REDIRECT_URI = os.getenv("MS_REDIRECT_URI", "")
MS_AUTHORITY = os.getenv("MS_AUTHORITY", f"https://login.microsoftonline.com/{MS_TENANT_ID}")
MS_SCOPES = os.getenv("MS_SCOPES", "openid profile offline_access Mail.Read")


def build_authorize_url(state: str) -> str:
    """
    Build the Microsoft login URL for Outlook OAuth.
    """
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
    """
    Exchange the authorization code for access + refresh tokens.
    """
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
