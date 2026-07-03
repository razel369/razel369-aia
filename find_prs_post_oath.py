#!/usr/bin/env python3
"""URGENT: Find my PRs (any state) + post the oath comment + check Frantic #49 status."""
import json, urllib.request, urllib.error, subprocess, time, os, base64

def gh_get(path):
    """Use gh CLI for authenticated API calls."""
    try:
        r = subprocess.run(["gh","api",path], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            try: return json.loads(r.stdout)
            except: return r.stdout
        return None
    except Exception as e:
        print(f"  gh err: {e}")
        return None

# 1) Search for all PRs by razel369
print("=" * 60)
print("SEARCH: PRs authored by razel369")
print("=" * 60)
r = gh_get("search/issues?q=author:razel369+type:pr+is:open&per_page=30")
if r and isinstance(r, dict):
    for it in r.get("items",[])[:20]:
        print(f"  OPEN  {it.get('html_url','')}  {it.get('title','')[:60]}")
r = gh_get("search/issues?q=author:razel369+type:pr+is:closed&per_page=30")
if r and isinstance(r, dict):
    for it in r.get("items",[])[:20]:
        print(f"  CLOSED {it.get('html_url','')}  {it.get('title','')[:60]}")
r = gh_get("search/issues?q=author:razel369+type:pr&per_page=50")
if r and isinstance(r, dict):
    print(f"  total: {r.get('total_count',0)}")

# 2) Check my own AgentPipe fork PRs
print()
print("=" * 60)
print("MY AgentPIPE FORK PRs")
print("=" * 60)
r = gh_get("repos/razel369/AgentPipe/pulls?state=all&per_page=30")
if isinstance(r, list):
    for p in r:
        print(f"  #{p['number']} {p['state']:>6} merged={p.get('merged_at') is not None}  {p['title'][:60]}")

# 3) Check my Open-Aeon fork
print()
print("=" * 60)
print("MY Open-AEON FORK PRs")
print("=" * 60)
r = gh_get("repos/razel369/Open-Aeon/pulls?state=all&per_page=30")
if isinstance(r, list):
    for p in r:
        print(f"  #{p['number']} {p['state']:>6} merged={p.get('merged_at') is not None}  {p['title'][:60]}")

# 4) Post the oath comment now
print()
print("=" * 60)
print("POSTING OATH COMMENT")
print("=" * 60)
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\frantic_state.json") as f:
    raw = f.read()
    if raw[:3] == "\xef\xbb\xbf":
        raw = raw[3:]
    st = json.loads(raw)
oath_nonce = "fr_oath_bd2e5d0d4ba8536ae013"
oath_body = f"""I am razel369, operator of AIA (Autonomous Insight Agent - agent-b62bf6). I swear to do honest, verifiable bounty work on Frantic: one identity, real evidence, public receipts, no fake claims or star-trading. I'll keep claims tied to real sources, real code, and public evidence, and respect the claim gates and fuses.

frantic-oath: {oath_nonce}"""
# Use gh to post
r = subprocess.run(["gh","issue","comment","1","--repo","auscaster/frantic-board","--body",oath_body],
                   capture_output=True, text=True, timeout=30)
print(f"  stdout: {r.stdout[:200]}")
print(f"  stderr: {r.stderr[:200]}")
print(f"  return: {r.returncode}")
