"""
Google OAuth 2.0 Authentication Module
---------------------------------------
Handles credential loading, token caching, and browser-based OAuth flow.
Scopes: Google Docs (read/write) + Gmail (compose drafts).
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth scopes required by the MCP server
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.compose",
]

# Paths relative to the project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# On Railway (or other cloud providers), use a persistent volume mounted at a configurable path.
# Defaults to BASE_DIR for local development.
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)

CREDENTIALS_FILE = os.path.join(DATA_DIR, "credentials.json")
TOKEN_FILE = os.path.join(DATA_DIR, "token.json")


def get_credentials() -> Credentials:
    """
    Return valid Google OAuth credentials.

    Flow:
      1. If token.json exists and is still valid → use it directly.
      2. If token.json exists but is expired → refresh it silently.
      3. Otherwise → launch the browser-based OAuth consent flow,
         then persist the new token to token.json for future runs.
    """
    creds: Credentials | None = None

    # ── Step 1: Try loading cached token ──────────────────────────
    if "GOOGLE_TOKEN_JSON" in os.environ:
        try:
            token_info = json.loads(os.environ["GOOGLE_TOKEN_JSON"])
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except json.JSONDecodeError:
            print("⚠️ Failed to parse GOOGLE_TOKEN_JSON environment variable.")
    elif os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # ── Step 2: Refresh or re-authenticate ────────────────────────
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("⟳  Refreshing expired token …")
            creds.refresh(Request())
        else:
            if "GOOGLE_CREDENTIALS_JSON" in os.environ:
                try:
                    client_config = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                except json.JSONDecodeError:
                    raise ValueError("Failed to parse GOOGLE_CREDENTIALS_JSON")
            elif not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Missing {CREDENTIALS_FILE} and GOOGLE_CREDENTIALS_JSON. "
                    "Download credentials from Google Cloud Console."
                )
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            
            print("🔐 Launching browser for Google OAuth consent …")
            creds = flow.run_local_server(port=0)

        # ── Step 3: Persist token for next time ───────────────────
        if "GOOGLE_TOKEN_JSON" not in os.environ:
            with open(TOKEN_FILE, "w") as token_file:
                token_file.write(creds.to_json())
            print(f"✅ Token saved to {TOKEN_FILE}")

    return creds
