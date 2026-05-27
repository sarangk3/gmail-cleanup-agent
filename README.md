# 📬 Gmail Cleanup Agent

An AI-powered inbox cleanup tool built with [Claude](https://claude.ai) and the Gmail MCP (Model Context Protocol) integration. It scans your Gmail inbox, uses AI to decide what is clutter and what is worth keeping, shows you the decisions for review, and then moves the selected emails to trash — all without you having to touch a single email manually.

---

## 🧠 How It Works

### The Problem
A busy inbox with 80+ emails per day becomes unmanageable fast. Within a week you can have 500+ unread emails — newsletters, stock tips, social notifications, promotions, automated alerts — burying the things that actually matter.

### The Solution
This agent connects directly to your Gmail account and does the heavy lifting:

1. **Scan** — Claude searches your inbox across multiple categories (promotions, newsletters, social notifications, no-reply senders, updates) and fetches up to 50 threads at a time.

2. **Analyze** — For each email thread, Claude reads the sender, subject, and preview, then decides:
   - **Delete** → newsletters, marketing, social alerts, automated notifications, stock spam, old receipts, travel promos
   - **Keep** → personal emails, emails needing a reply, financial documents, recent receipts, active event confirmations, job applications

3. **Review** — You see the full list with color-coded decisions (🔴 delete / 🟢 keep). You can flip any individual decision before anything is deleted.

4. **Execute** — After you confirm, Claude calls the Gmail API to move every flagged thread to Trash. Nothing is permanently deleted — Gmail keeps Trash for 30 days, so you can recover anything by mistake.

---

## 📋 What Gets Deleted (by default)

| Category | Examples |
|---|---|
| Newsletters | Washington Post, Business Insider, TLDR, Beehiiv |
| Stock spam | Trading Essentials Hub, Traders Pledge, Analyst Ratings |
| Promotions | Expedia, Lyft, REI, Xfinity, Coursera discount emails |
| Social notifications | LinkedIn profile views, group digests |
| Automated alerts | No-reply senders, app notifications |
| Old receipts | DoorDash orders older than 2 weeks |
| Event digests | Microsoft Reactor |

## ✅ What Always Gets Kept

- Personal emails from real people
- Emails that need a reply or action
- Financial statements, invoices, tax documents
- Receipts from the last 14 days
- Active event confirmations and hackathon registrations
- Job application updates (rejections, interviews, offers)
- Security alerts from Google
- Home buying, legal, or medical correspondence

---

## 🛠️ How It Was Built

This project was built interactively inside [Claude.ai](https://claude.ai) using:

- **Claude Sonnet** — the AI model that reads and classifies emails
- **Gmail MCP** — a Model Context Protocol integration that gives Claude direct (read + write) access to Gmail
- **Gmail API label method** — moving threads to Trash is done by adding the `TRASH` label to a thread via `label_thread`

No external servers, no OAuth dance, no local code to run. Claude handles everything natively through the MCP connection.

---

## 🚀 How to Use It

### Prerequisites
- A [Claude.ai](https://claude.ai) account (Pro or Team)
- Gmail connected as an MCP integration in Claude

### Steps

1. Open Claude.ai and make sure Gmail is connected under **Integrations**
2. Start a new conversation and paste this prompt:

```
Scan my Gmail inbox for clutter. Search across promotions, newsletters, social notifications, no-reply senders, and general inbox. For each thread decide whether to delete or keep it using these rules:

DELETE: newsletters, marketing/promo emails, social notifications, automated alerts, stock spam, shipping confirmations older than 2 weeks, any bulk/mass email.

KEEP: personal emails, anything needing a reply, financial or legal docs, receipts from the last 14 days, active event confirmations, job application emails.

Show me the full list of decisions. I will review and then tell you to confirm deletion.
```

3. Review the list Claude produces
4. Say **"go ahead and delete"** or adjust any decisions first
5. Repeat the scan as many times as needed to work through your backlog

### For a large backlog
Each scan processes ~50 threads. If you have 500+ emails, run the agent 10+ times in the same conversation. Claude remembers what it has already processed in the session.

---

## 📁 Project Structure

```
gmail-cleanup-agent/
├── README.md               # This file
├── cleanup_agent.py        # Standalone Python version (uses Gmail API directly)
└── prompt.md               # The exact prompt used with Claude
```

---

## 🐍 Standalone Python Version

If you want to run this without Claude, `cleanup_agent.py` uses the Gmail API directly with rule-based filtering (no AI, but fast and free).

**Setup:**
```bash
pip install google-auth google-auth-oauthlib google-api-python-client
python cleanup_agent.py
```

You will need a `credentials.json` file from [Google Cloud Console](https://console.cloud.google.com) with the Gmail API enabled.

---

## 📊 Results From Our First Session

| Round | Scanned | Deleted | Kept |
|---|---|---|---|
| Round 1 | 50 | 42 | 8 |
| Round 2 | 48 | 32 | 16 |
| **Total** | **98** | **74** | **24** |

Biggest sources of clutter: stock trading newsletters, Bullish Academy emails, Business Insider/TLDR daily digests, and travel/ride promo emails.

---

## ⚠️ Safety Notes

- All deletions go to **Trash**, not permanent delete. Gmail auto-purges Trash after 30 days.
- The agent never deletes emails marked as important by Gmail if they are personal or financial.
- You can always recover a trashed email within 30 days from the Gmail Trash folder.
- Revoke the Gmail MCP integration anytime from Claude Settings → Integrations.

---

## 🔮 Next Steps

- [ ] Build a Google Apps Script version that runs on a daily schedule automatically
- [ ] Add sender-based memory (auto-delete from senders you always trash)
- [ ] Unsubscribe links — not just delete, but actually unsubscribe from newsletters
- [ ] Weekly summary email of what was cleaned

---

## 📄 License

MIT — use freely, modify as you like.
