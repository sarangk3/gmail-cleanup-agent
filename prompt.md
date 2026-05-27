# Claude Prompt Guide

Use these prompts directly in Claude.ai with the Gmail MCP integration connected.

---

## Scan and Review Prompt

```
Scan my Gmail inbox for clutter. Search across the following categories:
- in:inbox
- category:promotions
- unsubscribe
- category:social
- noreply OR no-reply
- category:updates

For each thread, assign a recommendation of DELETE or KEEP using these rules:

DELETE: newsletters, marketing and promotional emails, social notifications (LinkedIn,
Facebook, Twitter), automated alerts, stock and trading spam, shipping confirmations
older than two weeks, travel and ride-share promos, course discount emails, daily
news digests, app notifications, and referral emails.

KEEP: personal emails from real people, emails requiring a reply or action, financial
documents (bank statements, invoices, tax documents), receipts from the last 14 days,
active event confirmations, job application updates (offers, rejections, interviews),
security alerts, and home buying, legal, or medical correspondence.

Present the full list with sender, subject, and your reason for each decision.
I will review and confirm before anything is deleted.
```

---

## Confirm Deletion

After reviewing the list:

```
Go ahead and delete everything marked for deletion.
```

---

## Useful Variations

**To review only the delete pile:**
```
Show me only the emails you flagged for deletion.
```

**To override a sender in bulk:**
```
Keep everything from [sender name or domain].
```

**To skip the review step entirely:**
```
Scan my inbox and delete all clutter automatically without showing me the list first.
```

---

## Tips

- Each scan processes approximately 50 threads. For a large backlog, run the scan multiple times in the same conversation.
- Decisions can be overridden individually during the review step before confirming deletion.
- After a few sessions, the pattern becomes predictable. At that point, switching to the auto-delete mode (no review) saves additional time.
- For fully automated daily cleanup, see `cleanup_agent.py` which runs independently of Claude using Gmail API rules.
