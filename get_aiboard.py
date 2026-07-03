#!/usr/bin/env python3
"""Get ai-bounty-board files + look at submission guidelines + identify vulnerabilities."""
import subprocess, json, base64

FILES = ["SUBMISSION_GUIDELINES.md", "README.md", "server.js", "persistent-map.js", "agent-client.js", "reputation.js", "browse-handler.js", "package.json"]

for f in FILES:
    print(f"\n==== {f} ====")
    r = subprocess.run(["gh","api",f"repos/owocki-bot/ai-bounty-board/contents/{f}"], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try:
            j = json.loads(r.stdout)
            content = base64.b64decode(j.get("content","")).decode("utf-8", errors="replace")
            print(content[:5000])
        except Exception as e:
            print(f"err: {e}")
    else:
        print(f"gh err: {r.stderr[:200]}")
