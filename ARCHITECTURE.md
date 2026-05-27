# Architecture

This document describes the system design of the Gmail Cleanup Agent, how each component interacts, and the reasoning behind key implementation decisions.

---

## High-Level Overview

```
+-------------------------------------------------------------+
|                     User (Claude.ai)                        |
|                                                             |
|   "Scan my inbox and show me what to delete"                |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
|                    Claude (AI Engine)                       |
|                                                             |
|  - Receives the request                                     |
|  - Calls Gmail MCP tools to fetch threads                   |
|  - Reads sender, subject, and snippet for each email        |
|  - Applies keep/delete classification                       |
|  - Returns structured decision list                         |
+---------------+-----------------------------+---------------+
                |                             |
                v                             v
+---------------------------+   +-----------------------------+
|     Gmail MCP Server      |   |     Review UI (in chat)     |
|                           |   |                             |
|  search_threads()         |   |  - Displays each email      |
|  label_thread(TRASH)      |   |  - Color-coded decisions    |
|                           |   |  - Toggle to override       |
|  OAuth-secured bridge     |   |  - Confirm triggers delete  |
|  between Claude and the   |   |                             |
|  Gmail API                |   |                             |
+---------------------------+   +-----------------------------+
```

---

## Components

### 1. Claude (AI Classification Engine)

Claude is the core of the agent. Rather than applying keyword rules, it reads the actual content of each thread — sender, subject line, and snippet — and makes a contextual judgment.

**Responsibilities:**
- Runs multiple Gmail search queries to pull emails across categories
- Reads thread metadata (full body is not required — sender, subject, and snippet are sufficient)
- Assigns a keep or delete recommendation with a short reason
- Executes the trash operation by calling `label_thread` for each flagged thread

**Why Claude instead of rule-based filtering:**
A keyword filter cannot reliably distinguish between a Chase fraud alert (keep) and a Chase referral bonus email (delete), even though both originate from the same domain. Claude understands intent and context in a way that static rules cannot replicate.

---

### 2. Gmail MCP (Integration Layer)

MCP stands for Model Context Protocol — Anthropic's standard for giving Claude structured, authenticated access to external services.

The Gmail MCP server acts as a secure bridge between Claude and the Gmail API. Claude does not handle credentials directly. The flow is:

1. The user authorizes the Gmail MCP integration in Claude Settings.
2. The MCP server holds the OAuth token on behalf of the user.
3. Claude calls MCP tools as function calls, and the MCP server translates them into authenticated Gmail API requests.

**Tools used:**

| Tool | Purpose |
|---|---|
| `search_threads` | Search inbox using Gmail query syntax, returns thread list with metadata |
| `label_thread` | Apply a label to a thread — used to apply the TRASH label |

**Why MCP instead of direct API access:**
- Credentials are never exposed in Claude's context window
- OAuth 2.0 with scoped access (only what is needed)
- The integration can be revoked at any time from Claude Settings

---

### 3. Review UI

The review step is a lightweight HTML and JavaScript widget rendered inline in the Claude chat. It is a display and interaction layer only — it makes no API calls.

**How it works:**
- Claude fetches and classifies all emails server-side
- The decision data is embedded directly into the widget as a JavaScript array
- Each email is rendered as a row with a color-coded left border (red for delete, green for keep)
- Toggling a decision updates local state only
- The confirm button sends a message back to Claude with the finalized list of thread IDs to delete

**Why this approach:**
The widget does no networking. All intelligence and API access lives in Claude. This avoids CORS issues, keeps credentials out of the browser, and ensures the UI functions correctly inside sandboxed iframe environments.

---

## Data Flow

```
Step 1: Scan
--------------------------------------------------------------
User requests inbox scan
  |
  +-- Claude calls search_threads("category:promotions in:inbox")
  +-- Claude calls search_threads("unsubscribe")
  +-- Claude calls search_threads("category:social")
  +-- Claude calls search_threads("noreply OR no-reply")
  +-- Claude calls search_threads("in:inbox")
  |
  Each call returns: thread_id, subject, sender, date, snippet
  Claude deduplicates results across queries
  Claude assigns: { recommendation: "delete" | "keep", reason: "..." }

Step 2: Review
--------------------------------------------------------------
Claude passes the classified list to the Review UI widget
  |
  +-- Widget renders one row per email
  +-- User overrides individual decisions as needed
  +-- User clicks Confirm and Delete
  |
  Widget sends message to Claude: "Delete these thread IDs: [...]"

Step 3: Execute
--------------------------------------------------------------
Claude receives the confirmed delete list
  |
  +-- For each thread_id:
        Claude calls label_thread(threadId, labelIds=["TRASH"])
  |
  Gmail moves the thread to Trash (recoverable for 30 days)
  Claude reports: X deleted, Y kept
```

---

## Trash vs Permanent Delete

This agent applies the `TRASH` label via the Gmail API, equivalent to clicking Move to Trash in the Gmail UI. It does not call `threads.delete`.

- Trashed emails are recoverable for 30 days
- Gmail auto-purges Trash permanently after 30 days
- This behavior is intentional — it provides a recovery window for any misclassified emails

---

## Classification Logic

**Delete indicators:**
- Sender domain is a known bulk sender (newsletters, marketing platforms, social networks)
- Subject contains promotional language (percentage off, limited time, referral, discount)
- Email originates from a no-reply address with no actionable content
- Thread is a social notification (LinkedIn views, group digests)
- Thread is a news digest or daily newsletter
- Shipping confirmation or travel promo with no upcoming relevance

**Keep indicators:**
- Sender appears to be an individual (real name in the From field)
- Email relates to an active job application (rejection, interview, offer)
- Email is a financial document (statement, invoice, or receipt less than 14 days old)
- Email confirms an active event registration or ongoing engagement
- Email is a security alert from a major platform
- Thread contains back-and-forth replies indicating an ongoing conversation

**Default behavior:**
When uncertain, Claude defaults to keep. A false negative (leaving clutter) is less harmful than a false positive (trashing something important).

---

## Scaling

Each scan processes up to 50 threads (Gmail API limit per call). For a large backlog:

- Run multiple scans in the same session
- Claude tracks processed threads within the session context window
- A 500-email backlog requires approximately 10 scan rounds

For fully automated daily cleanup without Claude, see `cleanup_agent.py` — a standalone Python script using the Gmail API with rule-based filtering.

---

## Security Model

| Concern | Mitigation |
|---|---|
| Gmail credentials | Never exposed to Claude — managed by the MCP OAuth layer |
| API scope | Gmail MCP requests only the `gmail.modify` scope (read and label, no send) |
| Permanent deletion | Not possible through this agent — only the Trash label is applied |
| Revocation | Gmail MCP can be disconnected at any time in Claude Settings |

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI model | Claude Sonnet (claude-sonnet-4-20250514) |
| AI platform | Claude.ai |
| Gmail integration | Gmail MCP (OAuth 2.0) |
| Gmail operations | Gmail API v1 — threads.list, threads.modify |
| Review UI | HTML and vanilla JavaScript, rendered inline in Claude chat |
| Standalone fallback | Python 3, google-api-python-client |
| Repository | GitHub |
