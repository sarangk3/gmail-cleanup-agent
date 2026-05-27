# Architecture — Gmail Cleanup Agent

This document explains how the Gmail Cleanup Agent is structured, how the components talk to each other, and why it was built this way.

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User (Claude.ai)                     │
│                                                             │
│   "Scan my inbox and show me what to delete"                │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Claude (AI Brain)                      │
│                                                             │
│  • Receives the request                                     │
│  • Calls Gmail MCP tools to fetch threads                   │
│  • Reads sender, subject, snippet for each email            │
│  • Applies keep/delete logic                                │
│  • Returns structured decision list                         │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐    ┌─────────────────────────────┐
│      Gmail MCP Server    │    │     Review UI (in chat)     │
│                          │    │                             │
│  search_threads()        │    │  • Displays each email      │
│  label_thread(TRASH)     │    │  • Color-coded keep/delete  │
│                          │    │  • Toggle to flip decision  │
│  OAuth-secured bridge    │    │  • Confirm button triggers  │
│  between Claude and      │    │    the deletion phase       │
│  Gmail API               │    │                             │
└──────────────────────────┘    └─────────────────────────────┘
```

---

## Components

### 1. Claude (AI Decision Engine)

Claude is the brain of the agent. It is not just passing emails through a rules engine — it reads the actual content of each thread (sender, subject line, email snippet) and makes a judgment call based on context.

**What it does:**
- Runs multiple Gmail search queries in sequence to pull emails from different categories
- Reads each thread's metadata (no full body needed — sender + subject + snippet is enough)
- Decides keep vs delete based on trained understanding of what constitutes clutter
- Executes the trash operation by calling `label_thread` for each flagged thread

**Why Claude instead of simple rules:**
A rule-based filter (e.g. "delete anything from no-reply@") misses nuance. Claude can tell the difference between a Chase fraud alert (keep) and a Chase referral bonus email (delete), even though both come from chase.com. It understands context that keyword rules cannot.

---

### 2. Gmail MCP (The Bridge)

MCP stands for **Model Context Protocol** — Anthropic's standard for giving Claude secure, structured access to external services.

The Gmail MCP server acts as a secure bridge between Claude and the Gmail API. Claude never touches your Gmail credentials directly. Instead:

1. You authorize the Gmail MCP integration in Claude Settings
2. The MCP server holds the OAuth token
3. Claude calls MCP tools (like function calls), and the MCP server translates them into authenticated Gmail API requests

**Tools used in this project:**

| Tool | What it does |
|---|---|
| `search_threads` | Search inbox with Gmail query syntax, returns thread list with metadata |
| `label_thread` | Add a label to a thread — used to add `TRASH` label to delete |

**Why MCP instead of direct API:**
- No credentials stored in Claude's context
- OAuth 2.0 scoped access (only what's needed)
- Revocable at any time from Claude Settings → Integrations

---

### 3. Review UI

The review step is a lightweight HTML/JS widget rendered inline in the Claude chat. It is purely a display and interaction layer — it contains no API calls of its own.

**How it works:**
- Claude fetches and classifies all emails server-side
- The decision data is baked directly into the widget as a JavaScript array
- The UI renders each email as a row with a color-coded left border (red = delete, green = keep)
- Toggling a decision updates local state only
- The confirm button sends a message back to Claude with the final list of thread IDs to delete

**Why this approach:**
The widget does zero networking. All intelligence and API access lives in Claude. This avoids CORS issues, keeps credentials out of the browser, and means the UI works even in sandboxed iframe environments.

---

## Data Flow — Step by Step

```
Step 1: Scan
──────────────────────────────────────────────────────────────
User asks Claude to scan inbox
  │
  └─► Claude calls search_threads("category:promotions in:inbox")
  └─► Claude calls search_threads("unsubscribe")
  └─► Claude calls search_threads("category:social")
  └─► Claude calls search_threads("noreply OR no-reply")
  └─► Claude calls search_threads("in:inbox")
  │
  Each call returns: thread_id, subject, sender, date, snippet
  Claude deduplicates across queries
  Claude reads each result and assigns: { recommendation: "delete" | "keep", reason: "..." }

Step 2: Review
──────────────────────────────────────────────────────────────
Claude passes the classified list to the Review UI widget
  │
  └─► Widget renders one row per email
  └─► User can toggle any individual decision
  └─► User clicks "Confirm & Delete"
  │
  Widget sends message to Claude: "Delete these thread IDs: [...]"

Step 3: Execute
──────────────────────────────────────────────────────────────
Claude receives the confirmed delete list
  │
  └─► For each thread_id in the list:
        Claude calls label_thread(threadId, labelIds=["TRASH"])
  │
  Gmail moves the thread to Trash (recoverable for 30 days)
  Claude reports summary: X deleted, Y kept
```

---

## Delete vs Trash — Important Distinction

This agent does **not** permanently delete emails. It adds the `TRASH` label via the Gmail API, which is equivalent to clicking "Move to Trash" in the Gmail UI.

- Trashed emails are fully recoverable for **30 days**
- After 30 days, Gmail auto-purges them permanently
- If you want immediate permanent deletion, you would use the `threads.delete` endpoint instead — but that is intentionally not used here for safety

---

## Classification Logic

Claude applies the following logic when deciding keep vs delete:

**Delete signals:**
- Sender domain is a known bulk sender (newsletters, marketing platforms, social networks)
- Subject contains promotional language (% off, limited time, referral, discount)
- Email is from a no-reply address with no actionable content
- Thread is a social notification (LinkedIn views, group digests, Twitter alerts)
- Thread is a news digest or daily newsletter
- Shipping confirmation or travel promo with no upcoming relevance

**Keep signals:**
- Sender appears to be an individual person (real name in From field)
- Email relates to an active job application (rejection, interview, offer)
- Email is a financial document (statement, invoice, receipt <14 days old)
- Email is a confirmed event registration or active hackathon
- Email is a security alert from a major platform (Google, Apple, bank)
- Email is from a real estate agent, doctor, lawyer, or government address
- Thread has back-and-forth replies (indicates ongoing human conversation)

**Tie-breaking:**
When uncertain, Claude defaults to **keep**. It is better to leave a borderline email in the inbox than to accidentally trash something important.

---

## Scaling Considerations

Each scan processes ~50 threads (Gmail API limit per call). For a large backlog:

- Run multiple scans in the same conversation session
- Claude tracks what it has already processed within the session context
- A 500-email backlog requires ~10 scan rounds, taking roughly 5–10 minutes total

For fully automated daily cleanup without Claude involvement, see `cleanup_agent.py` — a standalone Python script using the Gmail API with rule-based filtering.

---

## Security Model

| Concern | How it is handled |
|---|---|
| Gmail credentials | Never exposed to Claude — held by MCP OAuth layer |
| Scope of access | Gmail MCP requests only `gmail.modify` scope (read + label, no send) |
| Permanent deletion | Not possible via this agent — only Trash label is applied |
| Revocation | Disconnect Gmail MCP anytime in Claude Settings → Integrations |
| Token exposure | GitHub token used to create this repo should be rotated after use |

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| AI model | Claude Sonnet (claude-sonnet-4-20250514) |
| AI platform | Claude.ai |
| Gmail integration | Gmail MCP (OAuth 2.0) |
| Gmail operations | Gmail API v1 — threads.list, threads.modify |
| Review UI | HTML + vanilla JS widget, rendered inline in Claude chat |
| Standalone fallback | Python 3 + google-api-python-client |
| Repository | GitHub (this repo) |
