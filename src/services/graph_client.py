import os
import requests
from datetime import datetime, timedelta

GRAPH_TENANT = os.getenv("GRAPH_TENANT_ID")
GRAPH_CLIENT = os.getenv("GRAPH_CLIENT_ID")
GRAPH_SECRET = os.getenv("GRAPH_CLIENT_SECRET")


class GraphClient:
    def __init__(self):
        self.token = None

    def get_token(self):
        url = f"https://login.microsoftonline.com/{GRAPH_TENANT}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": GRAPH_CLIENT,
            "client_secret": GRAPH_SECRET,
            "scope": "https://graph.microsoft.com/.default"
        }
        r = requests.post(url, data=data)
        r.raise_for_status()
        self.token = r.json()["access_token"]
        return self.token

    def list_emails(self, user="me", query=None):
        if not self.token:
            self.get_token()

        url = f"https://graph.microsoft.com/v1.0/{user}/messages"
        headers = {"Authorization": f"Bearer {self.token}"}

        params = {}
        if query:
            params["$search"] = query

        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()

    def get_last_week_emails(self, user="me"):
        if not self.token:
            self.get_token()

        one_week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"

        url = f"https://graph.microsoft.com/v1.0/{user}/messages"
        headers = {"Authorization": f"Bearer {self.token}"}

        params = {
            "$filter": f"receivedDateTime ge {one_week_ago}",
            "$top": 50
        }

        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()["value"]
