# 🔌 Google MCP Server

An MCP-style (Model Context Protocol) server built with **FastAPI** that integrates with **Google Docs** and **Gmail**. Every action requires human-in-the-loop terminal approval before execution.

## 📁 Project Structure

```
google-mcp-server/
├── server.py          → FastAPI app with tool endpoints
├── auth.py            → Google OAuth 2.0 authentication
├── docs_tool.py       → Google Docs tool (append content)
├── gmail_tool.py      → Gmail tool (create draft)
├── requirements.txt   → Python dependencies
├── .gitignore         → Keeps secrets out of version control
├── README.md          → This file
├── credentials.json   → ⚠️ NOT committed (download from Google Cloud)
└── token.json         → ⚠️ NOT committed (auto-generated after OAuth)
```

---

## 🛠️ Prerequisites

- **Python 3.10+**
- A **Google Cloud project** with the following APIs enabled:
  - Google Docs API
  - Gmail API

---

## 🚀 Setup

### 1. Clone & Install Dependencies

```bash
cd google-mcp-server
pip install -r requirements.txt
```

### 2. Create Google Cloud OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Navigate to **APIs & Services → Library** and enable:
   - **Google Docs API**
   - **Gmail API**
4. Go to **APIs & Services → Credentials**.
5. Click **+ CREATE CREDENTIALS → OAuth client ID**.
6. Choose **Desktop app** as the application type.
7. Download the JSON file and save it as **`credentials.json`** in the project root.

### 3. Run the Server

```bash
python server.py
```

On the **first run**, a browser window will open asking you to authorize the app with your Google account. After granting access:
- A `token.json` file is created automatically.
- Future runs will skip the browser flow and use the cached token.

The server starts at: **http://localhost:8000**

---

## 📡 API Endpoints

### `GET /`
Health check — returns server info and available tools.

### `POST /append_to_doc`
Append text to an existing Google Doc.

**Request body:**
```json
{
  "doc_id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
  "content": "Hello from MCP server!"
}
```

**How to find your `doc_id`:**
Open your Google Doc — the ID is in the URL:
```
https://docs.google.com/document/d/<THIS_IS_THE_DOC_ID>/edit
```

### `POST /create_email_draft`
Create a draft email in your Gmail account.

**Request body:**
```json
{
  "to": "recipient@example.com",
  "subject": "Meeting Notes",
  "body": "Hi, here are the notes from today's meeting."
}
```

---

## 🛡️ Human-in-the-Loop Approval

Every action prints its details to the **server terminal** and waits for manual approval:

```
════════════════════════════════════════════════════════════
🔔  ACTION REQUESTED: Append to Google Doc
────────────────────────────────────────────────────────────
   doc_id: 1aBcDeFgHiJkLmNoPqRsTuVwXyZ
   content: Hello from MCP server!
════════════════════════════════════════════════════════════
✋ Approve? (y/n): y
✅ Approved.
```

If denied (`n`), the endpoint returns a **403** error.

---

## 🧪 Testing with curl

```bash
# Health check
curl http://localhost:8000/

# Append to a Google Doc
curl -X POST http://localhost:8000/append_to_doc \
  -H "Content-Type: application/json" \
  -d '{"doc_id": "YOUR_DOC_ID", "content": "Appended via MCP!"}'

# Create a Gmail draft
curl -X POST http://localhost:8000/create_email_draft \
  -H "Content-Type: application/json" \
  -d '{"to": "test@example.com", "subject": "Test Draft", "body": "Created via MCP server."}'
```

You can also use the **interactive Swagger UI** at: **http://localhost:8000/docs**

---

## 📌 Notes

- **OAuth scopes used:**
  - `https://www.googleapis.com/auth/documents` — read/write Google Docs
  - `https://www.googleapis.com/auth/gmail.compose` — create Gmail drafts
- If you change scopes, delete `token.json` and re-authenticate.
- **Local run:** The server uses `input()` for terminal approval, so it must be run in an interactive terminal.
- **Production run:** If deployed (e.g. to Railway), set `REQUIRE_APPROVAL=false` to bypass the interactive terminal prompt.

---

## ☁️ Railway Deployment

This server can be easily deployed to [Railway](https://railway.app/). 

1. Ensure you have run the app locally at least once so `token.json` is generated.
2. In Railway, deploy this repository.
3. In your Railway **Variables** tab, add the following variables:
   - **`REQUIRE_APPROVAL`**: `false` (bypasses terminal prompts so the app doesn't crash)
   - **`GOOGLE_CREDENTIALS_JSON`**: Paste the entire contents of your local `credentials.json` file here.
   - **`GOOGLE_TOKEN_JSON`**: Paste the entire contents of your local `token.json` file here.
4. The provided `Procfile` will automatically start the server.
