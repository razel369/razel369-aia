#!/usr/bin/env python3
"""Get full server.js + key files to find security vulnerabilities for owk-005."""
import subprocess, json, base64

def get_file(path):
    r = subprocess.run(["gh","api",f"repos/owocki-bot/ai-bounty-board/contents/{path}"], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try:
            j = json.loads(r.stdout)
            return base64.b64decode(j.get("content","")).decode("utf-8", errors="replace")
        except: pass
    return None

# Get the full server.js
content = get_file("server.js")
if content:
    print("=" * 60)
    print(f"SERVER.JS ({len(content)} chars)")
    print("=" * 60)
    print(content)
