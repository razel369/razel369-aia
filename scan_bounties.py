#!/usr/bin/env python3
"""Search for fresh USDC/ETH/USDT bounties created in last N days on GitHub."""
import json, sys, subprocess, datetime, os
os.environ['PYTHONIOUTF8'] = '1'

QUERIES = [
    "bounty USDC",
    "bounty USDT",
    "paid in USDC",
    "Algora",
    "[BOUNTY",
    "reward USDC",
    "crypto bounty",
    "agent bounty",
]

seen = set()
out = []
for q in QUERIES:
    print(f"=== Searching: {q!r} ===", file=sys.stderr)
    try:
        r = subprocess.run(
            ["gh", "search", "issues", q, "--state", "open",
             "--json", "number,title,url,createdAt,repository,labels,body",
             "--limit", "30"],
            capture_output=True, text=True, encoding='utf-8', timeout=60
        )
        if r.returncode != 0:
            print(f"  gh err: {r.stderr[:200]}", file=sys.stderr)
            continue
        data = json.loads(r.stdout)
        for it in data:
            key = f"{it['repository']['nameWithOwner']}#{it['number']}"
            if key in seen:
                continue
            seen.add(key)
            labels = ",".join(l['name'] for l in it.get('labels', []))
            usdc = 0
            t = it['title'].lower()
            for marker in ['$300','$280','$250','$220','$200','$180','$150','$100','$75','$50','$25','$23','$20','$10']:
                if marker in t:
                    try: usdc = max(usdc, int(marker.replace('$','')))
                    except: pass
            age_days = (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(it['createdAt'].replace('Z','+00:00'))).days
            out.append({
                "key": key,
                "title": it['title'][:120],
                "url": it['url'],
                "usdc": usdc,
                "labels": labels,
                "age_days": age_days,
                "created": it['createdAt'][:10],
            })
    except Exception as e:
        print(f"  err: {e}", file=sys.stderr)

out.sort(key=lambda x: (-x['usdc'], x['age_days']))
print(f"\n=== Top 30 by USDC value ===")
for r in out[:30]:
    print(f"  ${r['usdc']:>4}  {r['age_days']:>3}d  {r['key']:<50}  {r['title']}")
print(f"\n=== Freshest 15 (last 7 days) ===")
fresh = [r for r in out if r['age_days'] <= 7]
fresh.sort(key=lambda x: x['age_days'])
for r in fresh[:15]:
    print(f"  ${r['usdc']:>4}  {r['age_days']:>3}d  {r['key']:<50}  {r['title']}")

with open("data/bounty_scan.json","w", encoding="utf-8") as f:
    json.dump({"scanned_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "total": len(out), "items": out}, f, indent=2, ensure_ascii=False)
print(f"\nWrote data/bounty_scan.json with {len(out)} items")
