#!/usr/bin/env python3
"""
Expanded bounty scanner — covers platforms my v1 missed.
Sources: GitHub (Algora, Opire, GrantFox, TariProject, Eaprime1) + HN + AgentPipe issues.
"""
import json, sys, subprocess, datetime, os
os.environ['PYTHONIOUTF8'] = '1'
from urllib.request import urlopen, Request
from urllib.error import HTTPError

UA = "razel369-aia/1.0 (+https://razel369.github.io/aia/)"

# (query, label_filter, max_results)
QUERIES = [
    ("bounty USDC", "bounty", 50),
    ("bounty XLM", "bounty", 30),
    ("bounty XTM", "bounty", 20),
    ("bounty USDC Algora", None, 30),
    ("/reward bounty", None, 30),
    ("Opire bounty", "opire", 20),
    ("GrantFox bounty", "bounty", 30),
    ("[BOUNTY", None, 50),
    ("claim this bounty", None, 20),
    ("AI agent bounty", None, 20),
    ("PR review sub-agent", None, 10),
    ("bounty CHANGELOG", None, 10),
    ("bounty template", None, 10),
    ("bounty hook", None, 10),
    ("bounty skill", None, 10),
    ("first PR that passes review", None, 15),
    ("paid in USDC", None, 20),
    ("paid in XLM", None, 20),
    ("paid in XTM", None, 20),
    ("crypto bounty", None, 20),
]

seen = set()
items = []

for q, label, lim in QUERIES:
    print(f"  scan: {q!r}", file=sys.stderr)
    try:
        args = ["gh", "search", "issues", q, "--state", "open", "--json",
                "number,title,url,createdAt,repository,labels,body",
                "--limit", str(lim)]
        if label:
            args[1:1] = [f"label:{label}"]
        r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', timeout=60)
        if r.returncode != 0:
            print(f"    gh err: {r.stderr[:200]}", file=sys.stderr)
            continue
        for it in json.loads(r.stdout):
            key = f"{it['repository']['nameWithOwner']}#{it['number']}"
            if key in seen:
                continue
            seen.add(key)
            t = it['title'].lower()
            body = (it.get('body') or '').lower()
            usdc = xlm = xtm = xp = 0
            # Extract dollar amounts from title
            for marker, mult in [("$300",300),("$280",280),("$250",250),("$220",220),
                                  ("$200",200),("$180",180),("$150",150),("$100",100),
                                  ("$75",75),("$50",50),("$25",25),("$23",23),("$20",20),
                                  ("$15",15),("$10",10)]:
                if marker in t:
                    usdc = max(usdc, mult)
            # XLM: 5, 10, 15, 20, 25, 50
            for m in [5, 10, 15, 20, 25, 50, 100, 200, 500, 1000]:
                if f"{m} xlm" in t or f"{m}xlm" in t or f"xlm {m}" in body[:200]:
                    xlm = max(xlm, m)
            # XTM: 15000, 1000, 500, 200, 100
            for m in [50, 100, 200, 500, 1000, 5000, 15000]:
                if f"{m} xtm" in t or f"{m}xtm" in t or f"xtm {m}" in body[:300]:
                    xtm = max(xtm, m)
            # XP (custos)
            for m in [50, 100, 150, 200, 500, 1000]:
                if f"{m} xp" in t or f"xp reward" in body[:200] or f"{m}xp" in t:
                    xp = max(xp, m)
            age = (datetime.datetime.now(datetime.timezone.utc) -
                   datetime.datetime.fromisoformat(it['createdAt'].replace('Z','+00:00'))).days
            items.append({
                "key": key,
                "repo": it['repository']['nameWithOwner'],
                "number": it['number'],
                "title": it['title'][:140],
                "url": it['url'],
                "labels": ",".join(l['name'] for l in it.get('labels', [])),
                "usdc": usdc, "xlm": xlm, "xtm": xtm, "xp": xp,
                "age_days": age,
                "created": it['createdAt'][:10],
                "summary": (it.get('body') or '')[:300],
            })
    except Exception as e:
        print(f"    err: {e}", file=sys.stderr)

# Score: USDC is the target, then XTM, XLM, XP. Newer = slightly better.
def score(x):
    s = (x['usdc']*1000 + x['xtm']*0.5 + x['xlm']*0.2 + x['xp']*0.1)
    return s - x['age_days']*0.1

items.sort(key=score, reverse=True)

print(f"\n=== TOP 40 BY SCORE (USDC=1000x, XTM=0.5x, XLM=0.2x, XP=0.1x, age penalty 0.1/day) ===")
for r in items[:40]:
    val = ""
    if r['usdc']: val += f"${r['usdc']} "
    if r['xtm']: val += f"{r['xtm']}XTM "
    if r['xlm']: val += f"{r['xlm']}XLM "
    if r['xp']: val += f"{r['xp']}XP "
    print(f"  {val:>14}  {r['age_days']:>3}d  {r['key']:<45}  {r['title'][:80]}")

# Highlight AI-agent-friendly: title contains "agent", "ai", "skill", "claude", "workflow", "template", "hook", "review"
print(f"\n=== AI-AGENT-FRIENDLY (text-match filter) ===")
ai_kw = ["agent", "ai ", "ai-", "claude", "skill", "workflow", "template", "hook", "review",
         "changelog", "skill:", "sub-agent", "mcp"]
for r in items:
    blob = (r['title'] + " " + r['summary']).lower()
    if any(k in blob for k in ai_kw):
        val = ""
        if r['usdc']: val += f"${r['usdc']} "
        if r['xtm']: val += f"{r['xtm']}XTM "
        if r['xlm']: val += f"{r['xlm']}XLM "
        if r['xp']: val += f"{r['xp']}XP "
        print(f"  {val:>14}  {r['age_days']:>3}d  {r['key']:<45}  {r['title'][:80]}")

with open("data/bounty_scan_v2.json", "w", encoding="utf-8") as f:
    json.dump({
        "scanned_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total": len(items),
        "items": items,
    }, f, indent=2, ensure_ascii=False)
print(f"\nWrote data/bounty_scan_v2.json with {len(items)} items")
