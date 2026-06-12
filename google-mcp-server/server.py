"""
MCP-Style Server — Google Docs + Gmail
----------------------------------------
FastAPI application with human-in-the-loop approval.
Every action is printed to the terminal and requires manual 'y' confirmation
before the Google API call is executed.
"""

import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from docs_tool import append_to_doc
from gmail_tool import create_email_draft

# ── FastAPI app ───────────────────────────────────────────────────
app = FastAPI(
    title="Google MCP Server",
    description="MCP-style server with human-in-the-loop approval for Google Docs and Gmail actions.",
    version="1.0.0",
)


# ── Request schemas ───────────────────────────────────────────────
class AppendDocRequest(BaseModel):
    doc_id: str
    content: str


class CreateDraftRequest(BaseModel):
    to: str
    subject: str
    body: str


# ── Human-in-the-loop approval ────────────────────────────────────
def request_approval(action_name: str, payload: dict) -> bool:
    """
    Print the pending action to the terminal and wait for operator approval.
    Returns True only if the operator types 'y' or 'yes'.
    """
    import os
    if os.environ.get("REQUIRE_APPROVAL", "true").lower() == "false":
        print(f"🔔 ACTION AUTO-APPROVED (REQUIRE_APPROVAL=false): {action_name}")
        return True

    print("\n" + "═" * 60)
    print(f"🔔  ACTION REQUESTED: {action_name}")
    print("─" * 60)
    for key, value in payload.items():
        # Truncate long values for readability
        display = str(value)
        if len(display) > 200:
            display = display[:200] + " …"
        print(f"   {key}: {display}")
    print("═" * 60)

    try:
        answer = input("✋ Approve? (y/n): ").strip().lower()
    except EOFError:
        # Non-interactive environment — deny by default
        print("⚠️  Non-interactive terminal detected. Action DENIED.")
        return False

    approved = answer in ("y", "yes")
    print("✅ Approved." if approved else "❌ Denied.")
    return approved


# ── Endpoints ─────────────────────────────────────────────────────
@app.post("/append_to_doc")
def endpoint_append_to_doc(req: AppendDocRequest):
    """Append text to a Google Doc (requires terminal approval)."""
    payload = {"doc_id": req.doc_id, "content": req.content}

    if not request_approval("Append to Google Doc", payload):
        raise HTTPException(status_code=403, detail="Action denied by operator.")

    try:
        result = append_to_doc(req.doc_id, req.content)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/create_email_draft")
def endpoint_create_email_draft(req: CreateDraftRequest):
    """Create a Gmail draft (requires terminal approval)."""
    payload = {"to": req.to, "subject": req.subject, "body": req.body}

    if not request_approval("Create Gmail Draft", payload):
        raise HTTPException(status_code=403, detail="Action denied by operator.")

    try:
        result = create_email_draft(req.to, req.subject, req.body)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Health check ──────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "server": "Google MCP Server",
        "version": "1.0.0",
        "tools": [
            {"name": "append_to_doc", "method": "POST", "path": "/append_to_doc"},
            {"name": "create_email_draft", "method": "POST", "path": "/create_email_draft"},
        ],
    }


# ── Entry point ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting Google MCP Server on http://localhost:8000")
    print("📖 Interactive docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
