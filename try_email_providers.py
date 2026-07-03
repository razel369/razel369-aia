#!/usr/bin/env python3
"""Try multiple email providers + try real-domain emails."""
import json, urllib.request, urllib.error

def fetch(method, url, data=None, headers=None):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json, text/event-stream"}
    if headers: h.update(headers)
    body = None
    if data is not None:
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode("utf-8", errors="replace")
            try:
                return r.status, json.loads(text)
            except:
                return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(text)
        except:
            return e.code, text
    except Exception as e:
        return -1, str(e)

# Try mail.tm
print("=" * 60)
print("mail.tm: create account")
print("=" * 60)
s, d = fetch("POST", "https://api.mail.tm/accounts", {
    "address":"razel369aia@protonmail.com",
    "password":"AiaX402Bot2026!"
})
print(f"status: {s}, resp: {d}")

# Try alternative disposable APIs
print()
print("=" * 60)
print("Try alternative: api.guerrillamail.com")
print("=" * 60)
s, d = fetch("GET", "https://api.guerrillamail.com/ajax.php?f=get_email_address&lang=en&site=guerrillamail.com&sid=")
print(f"status: {s}, resp: {d}")

# Try temp-mail.io API
print()
print("=" * 60)
print("Try temp-mail.io: get email")
print("=" * 60)
s, d = fetch("GET", "https://api.internal.temp-mail.io/api/v3/email/new", data=None)
print(f"status: {s}, resp: {d}")

# Try tempmail.com
print()
print("=" * 60)
print("Try tempmail.lol")
print("=" * 60)
s, d = fetch("GET", "https://api.tempmail.lol/v1/inbox/create", data=None)
print(f"status: {s}, resp: {d}")

# Try disposable services
print()
print("=" * 60)
print("Try getnada.com")
print("=" * 60)
s, d = fetch("GET", "https://api.getnada.com/api/v1/inboxes/new", data=None)
print(f"status: {s}, resp: {d}")
