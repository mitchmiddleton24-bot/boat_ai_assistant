# src/outlook_reader.py

import requests
from msal import ConfidentialClientApplication
import os

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

# Get access token
def get_token():
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Failed to acquire token", result)

# Read emails from inbox
def read_emails():
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = "https://graph.microsoft.com/v1.0/users/YOUR_EMAIL_HERE/messages?$top=10"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        emails = []
        for msg in data.get("value", []):
            emails.append({
                "subject": msg.get("subject"),
                "from": msg.get("from", {}).get("emailAddress", {}).get("address"),
                "body_preview": msg.get("bodyPreview")
            })
        return emails
    else:
        raise Exception(f"Error reading emails: {response.status_code} - {response.text}")
