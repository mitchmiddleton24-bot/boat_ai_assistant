# src/outlook_reader.py

import os
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv

# Load .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

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
        raise Exception(f"Token failure: {result}")
    print("Access token granted:", result.get("access_token"))

# Read emails
def read_emails():
    token = get_token()

    # Print first 60 characters of token for sanity check
    print("Access token:", token[:60])

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = "https://graph.microsoft.com/v1.0/users/mitchconstructiondev@outlook.com/mailFolders/Inbox/messages?$top=5"

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
