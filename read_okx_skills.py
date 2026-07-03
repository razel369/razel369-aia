#!/usr/bin/env python3
"""Read OKX OnchainOS skills READMEs to find earning opportunities + explore OKX AI tasks."""
import subprocess, os

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")

# Use gh api to read the skill files
KEY_SKILLS = [
    "skills/okx-agent-task",
    "skills/okx-agent-payments-protocol",
    "skills/okx-agentic-wallet",
    "skills/okx-agent-identity",
    "skills/okx-growth-competition",
    "skills/okx-onchain-gateway",
    "skills/okx-agent-chat",
    "skills/okx-defi-invest",
    "skills/okx-dex-signal",
    "README.md",
    "AGENTS.md",
    "package.json",
    "cli"
]

for s in KEY_SKILLS:
    print("=" * 70)
    print(f"FILE: {s}")
    print("=" * 70)
    r = subprocess.run(["gh","api",f"repos/okx/onchainos-skills/contents/{s}"],
                       capture_output=True, text=True, timeout=20)
    if r.returncode == 0:
        try:
            j = json.loads(r.stdout)
            if j.get("type") == "dir":
                # List the directory
                r2 = subprocess.run(["gh","api",f"repos/okx/onchainos-skills/contents/{s}"],
                                    capture_output=True, text=True, timeout=20)
                if r2.returncode == 0:
                    items = json.loads(r2.stdout)
                    print(f"  DIR with {len(items)} items:")
                    for it in items[:20]:
                        print(f"    {it.get('type','?'):4s} {it.get('name','?')}")
            else:
                content_b64 = j.get("content", "")
                if content_b64:
                    import base64
                    content = base64.b64decode(content_b64).decode("utf-8", errors="replace")
                    print(f"  ({len(content)} chars)")
                    print(content[:3000])
                else:
                    print(f"  empty")
        except Exception as e:
            print(f"  ERR: {e}")
    else:
        print(f"  ERR: {r.stderr[:200]}")
    print()
