"""
Gmail Tool — Create Draft
---------------------------
Creates a draft email in the authenticated user's Gmail account.
Uses the Gmail API's drafts.create endpoint.
"""

import base64
from email.mime.text import MIMEText

# pyrefly: ignore [missing-import]
from googleapiclient.discovery import build
from auth import get_credentials


def create_email_draft(to: str, subject: str, body: str) -> dict:
    """
    Create a Gmail draft addressed to *to* with the given *subject* and *body*.

    Steps:
      1. Authenticate and build the Gmail service.
      2. Construct a MIME message.
      3. Base64url-encode it (required by the Gmail API).
      4. Call drafts.create to save the draft.
      5. Return a summary dict with the draft ID.

    Raises:
        googleapiclient.errors.HttpError: If the API call fails
            (e.g. quota exceeded, invalid credentials).
    """
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    # ── Build MIME message ────────────────────────────────────────
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    # Gmail API expects base64url-encoded RFC 2822 message bytes
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    # ── Create the draft ──────────────────────────────────────────
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body={"message": {"raw": raw}})
        .execute()
    )

    return {
        "status": "success",
        "draft_id": draft["id"],
        "to": to,
        "subject": subject,
    }
