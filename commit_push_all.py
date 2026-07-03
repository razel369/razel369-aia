#!/usr/bin/env python3
"""Commit + push all uncommitted changes to razel369-aia."""
import subprocess, os, time

os.chdir(r"C:\Users\rmalk\projects\razel369-aia")

# Add everything
r = subprocess.run(["git","add","-A"], capture_output=True, text=True, timeout=30)
print(f"add: rc={r.returncode}, stderr={r.stderr[:300]}")

# What's being added?
r = subprocess.run(["git","status","--short"], capture_output=True, text=True, timeout=10)
files = r.stdout.strip().split('\n')
print(f"\nfiles to commit: {len(files)}")
for f in files[:30]:
    print(f"  {f}")
if len(files) > 30:
    print(f"  ... and {len(files)-30} more")

# Commit
msg = f"""Snapshot money check {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

Automated state snapshot. Includes:
- All helper scripts built today
- AIA dashboard + worker source
- Audit + badge deliverables
- Agent loops + monitors
- Feed + history JSONs

This is a checkpoint, not a code change.
"""
r = subprocess.run(["git","commit","-m",msg], capture_output=True, text=True, timeout=30)
print(f"\ncommit: rc={r.returncode}")
print(f"  stdout: {r.stdout[:200]}")
print(f"  stderr: {r.stderr[:300]}")

# Push
r = subprocess.run(["git","push","origin","main"], capture_output=True, text=True, timeout=120)
print(f"\npush: rc={r.returncode}")
print(f"  stdout: {r.stdout[:300]}")
print(f"  stderr: {r.stderr[:500]}")

# Verify
r = subprocess.run(["git","log","--oneline","-3"], capture_output=True, text=True, timeout=10)
print(f"\nlast 3 commits:\n{r.stdout}")

r = subprocess.run(["git","status","--short"], capture_output=True, text=True, timeout=10)
remaining = r.stdout.strip()
print(f"\nremaining: {remaining if remaining else 'CLEAN'}")
