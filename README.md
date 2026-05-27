# Gmail Cleanup Agent

An AI-powered inbox cleanup tool built with [Claude](https://claude.ai) and the Gmail MCP (Model Context Protocol) integration. It scans your Gmail inbox, classifies each thread as clutter or worth keeping, presents the decisions for review, and moves selected emails to Trash — without manually touching a single message.

---

## How It Works

### The Problem

A high-volume inbox — 80 or more emails per day — becomes unmanageable quickly. Within a week, newsletters, stock tips, social notifications, promotions, and automated alerts bury the messages that actually matter.

### The Solution

The agent connects directly to Gmail and handles the entire process:

1. **Scan** — Claude searches the inbox across multiple categories (promotions, newsletters, social notifications, no-reply senders, updates) and fetches up to 50 threads per run.

2. **Classify** — For each thread, Claude reads the sender, subject, and preview, then decides:
   - **Delete** — newsletters, marketing, social alerts, automated notifications, stock spam, old receipts, travel promos
   - **Keep** — personal emails, emails requiring action, financial documents, recent receipts, active event confirmations, job application correspondence

3. **Review** — A full list of decisions is presented with color-coded indicators. Any individual decision can be overridden before deletion runs.

4. **Execute** — On confirmation, Claude calls the Gmail API to move every flagged thread to Trash. Nothing is permanently deleted — Gmail retains Trash for 30 days.

---

## What Gets Deleted

| Category | Examples |
|---|---|
| Newsletters | Washington Post, Business Insider, TLDR, Beehiiv |
| Stock and trading spam | Trading Essentials Hub, Traders Pledge, Analyst Ratings |
| Promotions | Expedia, Lyft, REI, Xfinity, Coursera discount emails |
| Social notifications | LinkedIn profile views, group digests |
| Automated alerts | No-reply senders, app notifications |
| Old receipts | Food delivery orders older than two weeks |
| Event digests | Meetup group announcements, Microsoft Reactor |

## What Always Gets Kept

- Personal emails from real people
- Emails requiring a reply or action
- Financial statements, invoices, and tax documents
- Receipts from the last 14 days
- Active event confirmations and hackathon registrations
- Job application updates (rejections, interviews, offers)
- Security alerts from Google and financial institutions
- Home buying, legal, or medical correspondence

---

## How It Was Built

This project was built interactively inside [Claude.ai](https://claude.ai) using:

- **Claude Sonnet** — reads and classifies each email thread
- **Gmail MCP** — a Model Context Protocol integration that gives Claude secure, scoped access to Gmail
- **Gmail API label method** — deletion is performed by applying the `TRASH` label via `label_thread`

No external servers, no local code to run. Claude handles everything natively through the MCP connection.

---

## How to Use It

### Prerequisites

- A [Claude.ai](https://claude.ai) account (Pro or Team)
- Gmail connected as an MCP integration in Claude Settings

### Steps

1. Open Claude.ai and confirm Gmail is connected under Integrations.
2. Start a new conversation and use the prompt in `prompt.md`.
3. Review the list Claude produces.
4. Confirm deletion or adjust individual decisions first.
5. Repeat the scan as needed to work through a larger backlog.

For a backlog of 500 or more emails, each scan handles around 50 threads. Running the agent 10 times clears the full backlog in a single session.

---

## Project Structure

```
gmail-cleanup-agent/
├── README.md               This file
├── ARCHITECTURE.md         System design and component breakdown
├── prompt.md               Prompt templates for use with Claude
└── cleanup_agent.py        Standalone Python version using the Gmail API directly
```

---

## Standalone Python Version

`cleanup_agent.py` uses the Gmail API directly with rule-based filtering. No Claude required — useful for scheduled or automated runs.

**Setup:**
```bash
pip install google-auth google-auth-oauthlib google-api-python-client
python cleanup_agent.py
```

A `credentials.json` file is required from [Google Cloud Console](https://console.cloud.google.com) with the Gmail API enabled.

---

## Results from Initial Session

| Round | Scanned | Deleted | Kept |
|---|---|---|---|
| Round 1 | 50 | 42 | 8 |
| Round 2 | 48 | 32 | 16 |
| Total | 98 | 74 | 24 |

Primary sources of clutter: stock trading newsletters, daily news digests (Business Insider, TLDR), travel and ride-share promos, and financial marketing emails.

---

## Safety Notes

- All deletions go to Trash, not permanent delete. Gmail auto-purges Trash after 30 days.
- The agent defaults to keeping any email where the decision is ambiguous.
- Trashed emails can be recovered within 30 days from the Gmail Trash folder.
- The Gmail MCP integration can be revoked at any time from Claude Settings under Integrations.

---

## Planned Improvements

- Google Apps Script version that runs on a daily schedule without manual intervention
- Sender-based memory to auto-delete from addresses consistently marked as clutter
- Unsubscribe automation — not just delete, but remove from mailing lists
- Weekly digest summarizing what was cleaned

---

## License

MIT
