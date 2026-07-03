#!/usr/bin/env python3
"""Build comprehensive owk-005 security audit report + submit as PR."""
import subprocess, json, re, os

# 1) Look at the agent-client.js and reputation.js for more issues
def get_file(path):
    r = subprocess.run(["gh","api",f"repos/owocki-bot/ai-bounty-board/contents/{path}"], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try:
            j = json.loads(r.stdout)
            import base64
            return base64.b64decode(j.get("content","")).decode("utf-8", errors="replace")
        except: pass
    return None

with open(r"C:\Users\rmalk\projects\razel369-aia\server_full.js", "r", encoding="utf-8") as f:
    server = f.read()
agent_client = get_file("agent-client.js") or ""
reputation = get_file("reputation.js") or ""
persistent_map = get_file("persistent-map.js") or ""
browse_handler = get_file("browse-handler.js") or ""

print(f"server.js: {len(server)} chars")
print(f"agent-client.js: {len(agent_client)} chars")
print(f"reputation.js: {len(reputation)} chars")
print(f"persistent-map.js: {len(persistent_map)} chars")
print(f"browse-handler.js: {len(browse_handler)} chars")

# Look for additional issues
print()
print("=" * 60)
print("agent-client.js — content")
print("=" * 60)
print(agent_client[:5000])
