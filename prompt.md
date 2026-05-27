# Gmail Cleanup Agent — Claude Prompt

Use this prompt directly in Claude.ai with Gmail MCP connected.

---

## Scan & Review Prompt

```
Scan my Gmail inbox for clutter. Search across these categories using Gmail search:
- in:inbox
- category:promotions
- unsubscribe
- category:social
- noreply OR no-reply
- category:updates

For each thread, decide DELETE or KEEP:

DELETE: newsletters, marketing/promo emails, social notifications (LinkedIn, Facebook, Twitter),
automated alerts, stock/trading spam, shipping confirmations older than 2 weeks,
travel promos, ride-share discounts, airline offers, course discount emails,
daily news digests, substack newsletters, app notifications, referral emails.

KEEP: personal emails from real people, emails needing a reply or action,
financial documents (bank statements, invoices, tax docs),
receipts from the last 14 days, active event confirmations, job application emails
(offers, rejections, interviews), security alerts, home buying / legal / medical emails.

Show me the full list with sender, subject, and your reason. I will review and confirm.
```

---

## Confirm Deletion Prompt

After reviewing the list, say:

```
Go ahead and delete everything marked for deletion.
```

---

## Tips

- Run the scan multiple times to work through a large backlog (each scan handles ~50 emails)
- You can ask Claude to "only show me the delete pile" to review faster
- Say "keep everything from [sender]" to override in bulk
- After a few sessions, the pattern becomes predictable and you can switch to auto-delete mode
