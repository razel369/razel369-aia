#!/usr/bin/env python3
"""Verify PR #39 + force push the new branch + check PR files."""
import subprocess, json

def gh(path):
    r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        try: return json.loads(r.stdout)
        except: return r.stdout
    return None

# Check PR #39
pr = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/pulls/39")
if isinstance(pr, dict):
    print(f"PR #39:")
    print(f"  state: {pr.get('state')}")
    print(f"  title: {pr.get('title')}")
    print(f"  additions: {pr.get('additions')}")
    print(f"  deletions: {pr.get('deletions')}")
    print(f"  changed_files: {pr.get('changed_files')}")
    print(f"  head: {pr.get('head',{}).get('ref')}")
    print(f"  base: {pr.get('base',{}).get('ref')}")

# Get files
files = gh("repos/cyrilawoyemi99-max/owockibot-bounty-sync-/pulls/39/files")
if isinstance(files, list):
    print(f"\n  Files:")
    for f in files[:10]:
        print(f"    {f.get('status')} {f.get('filename')} +{f.get('additions')}/-{f.get('deletions')}")
