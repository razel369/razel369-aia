#!/usr/bin/env python3
"""Read OKX OnchainOS skill SKILL.md files."""
import subprocess, os, json, base64

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")

# Each skill is a directory, find its SKILL.md
SKILLS = [
    "okx-agent-task",
    "okx-agent-payments-protocol",
    "okx-agentic-wallet",
    "okx-agent-identity",
    "okx-growth-competition",
    "okx-onchain-gateway",
    "okx-agent-chat",
    "okx-defi-invest",
    "okx-dex-signal",
    "okx-ai-guide",
    "okx-how-to-play",
    "okx-task-watch",
    "okx-dapp-discovery",
    "okx-dex-swap",
    "okx-wallet-portfolio"
]

for s in SKILLS:
    print("=" * 70)
    print(f"SKILL: {s}")
    print("=" * 70)
    # List the skill directory
    r = subprocess.run(["gh","api",f"repos/okx/onchainos-skills/contents/skills/{s}"],
                       capture_output=True, text=True, timeout=20)
    if r.returncode == 0:
        try:
            items = json.loads(r.stdout)
            if isinstance(items, list):
                # Find SKILL.md
                skill_md = next((it for it in items if it.get("name", "").upper() == "SKILL.MD"), None)
                if not skill_md:
                    print(f"  no SKILL.md in {[it.get('name') for it in items]}")
                    # Just list files
                    for it in items[:5]:
                        print(f"    {it.get('type','?'):4s} {it.get('name','?')}")
                    continue
                # Read it
                path = skill_md.get("path")
                r2 = subprocess.run(["gh","api",f"repos/okx/onchainos-skills/contents/{path}"],
                                    capture_output=True, text=True, timeout=20)
                if r2.returncode == 0:
                    j = json.loads(r2.stdout)
                    content_b64 = j.get("content", "")
                    if content_b64:
                        content = base64.b64decode(content_b64).decode("utf-8", errors="replace")
                        print(f"  ({len(content)} chars)")
                        print(content[:2500])
                    else:
                        print(f"  empty")
            else:
                print(f"  unexpected response type: {type(items)}")
        except Exception as e:
            print(f"  ERR: {e}")
    else:
        print(f"  ERR: {r.stderr[:200]}")
    print()
