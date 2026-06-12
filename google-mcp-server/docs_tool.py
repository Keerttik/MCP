"""
Google Docs Tool — Append Content
----------------------------------
Appends plain-text content to the end of an existing Google Doc.
Uses the Docs API batchUpdate with an InsertText request.
"""

from googleapiclient.discovery import build
from auth import get_credentials


def append_to_doc(doc_id: str, content: str) -> dict:
    """
    Append *content* to the end of the Google Doc identified by *doc_id*.

    Steps:
      1. Authenticate and build the Docs service.
      2. Fetch the document to find the current end-of-body index.
      3. Insert the new text at that index (with a leading newline).
      4. Return a summary dict with the doc title and appended text.

    Raises:
        googleapiclient.errors.HttpError: If the API call fails
            (e.g. invalid doc_id, missing permissions).
    """
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    # ── Fetch document to determine the insertion index ───────────
    doc = service.documents().get(documentId=doc_id).execute()
    doc_title = doc.get("title", "Untitled")

    # The body content ends at this index (exclusive).
    # We insert at (endIndex - 1) to stay inside the body.
    body_content = doc.get("body", {}).get("content", [])
    end_index = body_content[-1]["endIndex"] if body_content else 1

    # ── Build the batchUpdate request ─────────────────────────────
    requests = [
        {
            "insertText": {
                "location": {"index": end_index - 1},
                "text": f"\n{content}",
            }
        }
    ]

    service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests},
    ).execute()

    return {
        "status": "success",
        "doc_id": doc_id,
        "doc_title": doc_title,
        "appended_text": content,
    }
