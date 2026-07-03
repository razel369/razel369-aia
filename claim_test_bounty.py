#!/usr/bin/env python3
"""
1. Fork jessedaustin93/Open-Aeon, update README, open PR (the $50 test bounty).
2. Inspect TariProject walletd code to estimate work for the 15,000 XTM bounty.
"""
import subprocess, json, sys, os, base64, time

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=kw.pop("timeout", 60))
    if kw.pop("check", False) and r.returncode != 0:
        print("CMD FAIL:", " ".join(cmd))
        print("STDERR:", r.stderr[:500])
        sys.exit(1)
    return r

# ============ STEP 1: Open-Aeon test bounty ============
print("=" * 60)
print("STEP 1: Open-Aeon test bounty")
print("=" * 60)

WORK = "C:/Users/rmalk/projects/open-aeon-bounty"
os.makedirs(WORK, exist_ok=True)

# Fork
print("Forking...")
r = run(["gh","repo","fork","jessedaustin93/Open-Aeon","--clone=false"])
print(r.stdout[:200], r.stderr[:200])

# Wait for fork to be ready
time.sleep(3)

# Clone
print("Cloning fork...")
if not os.path.isdir(WORK + "/Open-Aeon"):
    run(["gh","repo","clone","razel369/Open-Aeon", WORK + "/Open-Aeon"])

# Update README
readme_path = WORK + "/Open-Aeon/README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    cur = f.read()
print("Current README:", repr(cur))

new_readme = "# Open-Aeon\nAeon V1 integrated into Open Jarvis\n\n## Project status\nExperimental integration scaffold.\n"
if cur.strip() == "# Open-Aeon\nAeon V1 integrated into Open Jarvis".strip():
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)
    print("README updated.")
else:
    print("UNEXPECTED existing content - leaving as-is, appending section instead")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(cur.rstrip() + "\n\n## Project status\nExperimental integration scaffold.\n")

# Verify
with open(readme_path, "r", encoding="utf-8") as f:
    print("New README:", repr(f.read()))

# Commit + push
os.chdir(WORK + "/Open-Aeon")
run(["git","config","user.name","razel369"])
run(["git","config","user.email","razel369@users.noreply.github.com"])
run(["git","checkout","-b","add-project-status"])
run(["git","add","README.md"])
run(["git","commit","-m","Add Project status section per #1"])
run(["git","push","-u","origin","add-project-status"])

# Open PR
print("Opening PR...")
r = run(["gh","pr","create","--repo","jessedaustin93/Open-Aeon",
         "--base","main","--head","razel369:add-project-status",
         "--title","Add Project status section",
         "--body","Closes #1\n\nUpdates README.md with a `## Project status` section per the spec:\n- Existing title and description preserved\n- New section: `## Project status`\n- Content: `Experimental integration scaffold.`\n- Only README.md changed\n- Markdown clean, ends with newline"])
print(r.stdout)
print(r.stderr[:200])

# ============ STEP 2: TariProject inspection ============
print()
print("=" * 60)
print("STEP 2: TariProject walletd code inspection")
print("=" * 60)

# Check the actual file we need to edit
r = run(["gh","api","repos/tari-project/tari-ootle/contents/applications/tari_walletd/web_ui/src/routes/Wallet/Components/Accounts.tsx"])
if r.returncode == 0:
    d = json.loads(r.stdout)
    content = base64.b64decode(d.get("content","")).decode("utf-8", errors="replace")
    print(f"Accounts.tsx: {d.get('size',0)} bytes, {len(content.splitlines())} lines")
    # Print just first 80 lines + lines with 'account' or 'default'
    for i, line in enumerate(content.splitlines()[:120], 1):
        if any(k in line.lower() for k in ['account','default','star','badge','setdefault','isdefault']):
            print(f"  L{i:>4}  {line[:120]}")
    print("\n  --- raw first 80 lines ---")
    for i, line in enumerate(content.splitlines()[:80], 1):
        print(f"  {i:>4}  {line[:100]}")
else:
    print("err:", r.stderr[:300])
    # Try without src/
    r2 = run(["gh","api","repos/tari-project/tari-ootle/contents/applications/tari_walletd/web_ui/src/routes/Wallet/Components/"])
    if r2.returncode == 0:
        d2 = json.loads(r2.stdout)
        for f in d2:
            print(f"  {f.get('type','?'):<5}  {f.get('name','')}")
    else:
        print("deeper err:", r2.stderr[:300])

# Check the existing accountsSetDefault helper
print()
print("--- json_rpc.ts (look for accountsSetDefault) ---")
r = run(["gh","api","repos/tari-project/tari-ootle/contents/applications/tari_walletd/web_ui/src/utils/json_rpc.ts"])
if r.returncode == 0:
    d = json.loads(r.stdout)
    content = base64.b64decode(d.get("content","")).decode("utf-8", errors="replace")
    for i, line in enumerate(content.splitlines(), 1):
        if 'setDefault' in line or 'set_default' in line or 'accounts' in line.lower():
            print(f"  L{i:>4}  {line[:140]}")
else:
    print("err:", r.stderr[:200])
