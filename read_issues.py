#!/usr/bin/env python3
"""Read all claude-builders-bounty issues + TariProject + GrantFox samples."""
import subprocess, json, sys
os=None
issues = [
    "https://github.com/claude-builders-bounty/claude-builders-bounty/issues/1",
    "https://github.com/claude-builders-bounty/claude-builders-bounty/issues/2",
    "https://github.com/claude-builders-bounty/claude-builders-bounty/issues/3",
    "https://github.com/claude-builders-bounty/claude-builders-bounty/issues/4",
    "https://github.com/claude-builders-bounty/claude-builders-bounty/issues/5",
    "https://github.com/tari-project/tari-ootle/issues/2308",
    "https://github.com/Markp1598M/Helm/issues/1",
    "https://github.com/Eaprime1/custos/issues/187",
    "https://github.com/fluxerapp/fluxer-meta/issues/2",
    "https://github.com/fluxerapp/fluxer-meta/issues/5",
]
for u in issues:
    print(f"\n{'='*80}\n{u}\n{'='*80}")
    r = subprocess.run(["gh","issue","view",u,"--json","title,body,labels,state,comments,number"],
                       capture_output=True, text=True, encoding='utf-8', timeout=30)
    if r.returncode != 0:
        print("ERR:", r.stderr[:200])
        continue
    try:
        d = json.loads(r.stdout)
        print(f"Title: {d.get('title','')}")
        print(f"Labels: {[l['name'] for l in d.get('labels',[])]}")
        print(f"State: {d.get('state','')}  Comments: {len(d.get('comments',[]))}")
        body = d.get('body','') or ''
        print(f"Body ({len(body)} chars):")
        print(body[:2000])
        print('...')
        print(body[-400:] if len(body) > 2000 else '')
    except Exception as e:
        print("parse err:", e)
        print(r.stdout[:500])
