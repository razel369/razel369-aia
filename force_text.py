#!/usr/bin/env python3
"""Force git to track contributors.html as text + check encoding detection."""
import subprocess, os, json

# 1) Check .gitattributes and other markers
ag_path = r"C:\Users\rmalk\projects\AgentPipe\.gitattributes"
print(".gitattributes exists:", os.path.exists(ag_path))
if os.path.exists(ag_path):
    with open(ag_path, "r") as f:
        print(f.read()[:500])

# 2) Check current status + log
print()
print("Git log (last 3 commits):")
r = subprocess.run(["git","-C",r"C:\Users\rmalk\projects\AgentPipe","log","--oneline","-3"],
                   capture_output=True, text=True, timeout=30)
print(r.stdout)

# 3) Force re-add with text
print()
print("Force re-add with text:")
for cmd in [
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","rm","--cached","contributors.html"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","add","contributors.html"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","status"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","diff","--cached","--stat"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","commit","-m","Force re-add contributors.html as text (UTF-8)"],
    ["git","-C",r"C:\Users\rmalk\projects\AgentPipe","push","origin","contributors-page-1938","--force-with-lease"],
]:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print(f"  $ {' '.join(cmd[2:4])[:60]}")
    if r.stdout: print(f"    out: {r.stdout[:300]}")
    if r.stderr: print(f"    err: {r.stderr[:300]}")
    if r.returncode != 0: print(f"    RETURN: {r.returncode}")
