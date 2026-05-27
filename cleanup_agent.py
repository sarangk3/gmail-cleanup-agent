"""
Gmail Cleanup Agent — Standalone Python Version
Uses the Gmail API directly with rule-based filtering (no AI required).

Setup:
    pip install google-auth google-auth-oauthlib google-api-python-client
    
    Then get credentials.json from Google Cloud Console:
    1. Go to https://console.cloud.google.com
    2. Create a project, enable Gmail API
    3. Create OAuth 2.0 credentials (Desktop app)
    4. Download as credentials.json and place in this directory

Run:
    python cleanup_agent.py
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# ── Rules ─────────────────────────────────────────────────────────────────────

DELETE_SENDERS = [
    # Stock/trading spam
    "tradingessentialshub.com", "traderspledge.com", "stockmarketnewswire.com",
    "analystratings.net", "thetradingpub.com",
    # Travel promos
    "expedia.com", "lyftmail.com", "omanair.com", "contiki.com", "dollarflightclub.com",
    # Deal newsletters
    "emailbenefithub.com", "spartan.com", "preparedhero.com",
    # Finance marketing
    "bullish-academy.com", "kjbm.bullish-academy.com",
    # News digests
    "mail.beehiiv.com", "email.businessinsider.com", "tldrnewsletter.com",
    "fourhourbody.com", "substack.com",
]

DELETE_SUBJECT_KEYWORDS = [
    "unsubscribe", "% off", "deal", "discount", "limited time", "flash sale",
    "earn cash back", "referral", "newsletter", "weekly digest", "daily digest",
    "you're getting noticed", "viewed your profile", "job alert",
    "free audiobook", "upgrade now", "your reward",
]

KEEP_SENDERS = [
    "google.com", "accounts.google.com", "chase.com", "fidelity.com",
    "schwab.com", "irs.gov", "linkedin.com",  # keep actual messages not digests
]

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

# ── Decision logic ────────────────────────────────────────────────────────────

def should_delete(msg):
    headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
    sender = headers.get("from", "").lower()
    subject = headers.get("subject", "").lower()

    for domain in DELETE_SENDERS:
        if domain in sender:
            return True, f"sender matches delete list ({domain})"

    for kw in DELETE_SUBJECT_KEYWORDS:
        if kw in subject:
            return True, f"subject contains '{kw}'"

    return False, "no match — keeping"

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    service = get_service()
    print("Connected to Gmail.\n")

    queries = [
        "category:promotions in:inbox",
        "unsubscribe in:inbox",
        "category:social in:inbox",
        "noreply OR no-reply in:inbox",
    ]

    thread_ids_to_delete = []
    seen = set()

    for query in queries:
        result = service.users().threads().list(userId="me", q=query, maxResults=50).execute()
        threads = result.get("threads", [])
        print(f"Query '{query}': {len(threads)} threads")

        for t in threads:
            if t["id"] in seen:
                continue
            seen.add(t["id"])

            thread = service.users().threads().get(userId="me", id=t["id"], format="metadata").execute()
            msg = thread["messages"][0]
            delete, reason = should_delete(msg)

            headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
            subject = headers.get("subject", "(no subject)")[:60]
            sender = headers.get("from", "")[:40]

            status = "DELETE" if delete else "KEEP  "
            print(f"  [{status}] {sender:<40} | {subject} ({reason})")

            if delete:
                thread_ids_to_delete.append(t["id"])

    print(f"\n{'─'*60}")
    print(f"Found {len(thread_ids_to_delete)} threads to delete out of {len(seen)} scanned.")
    confirm = input("Type 'yes' to move them all to Trash: ").strip().lower()

    if confirm == "yes":
        for tid in thread_ids_to_delete:
            service.users().threads().trash(userId="me", id=tid).execute()
        print(f"✓ {len(thread_ids_to_delete)} threads moved to Trash.")
    else:
        print("Cancelled — nothing deleted.")

if __name__ == "__main__":
    main()
