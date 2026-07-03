#!/usr/bin/env python3
"""Check competition on each candidate bounty + discover less-contested ones."""
import subprocess, json

targets = [
    # tari-project
    "https://github.com/tari-project/tari-ootle/issues/2308",
    # cocohub-mobileapp
    "https://github.com/cocohub-mobileapp/cocohub-main/issues/47",
    "https://github.com/cocohub-mobileapp/cocohub-main/issues/48",
    "https://github.com/cocohub-mobileapp/cocohub-main/issues/49",
    "https://github.com/cocohub-mobileapp/cocohub-main/issues/50",
    "https://github.com/cocohub-mobileapp/cocohub-main/issues/51",
    "https://github.com/cocohub-mobileapp/cocohub-main/issues/52",
    # rustchain-bounties (look at small ones)
    "https://github.com/Scottcjn/rustchain-bounties/issues/14479",
    "https://github.com/Scottcjn/rustchain-bounties/issues/14480",
    "https://github.com/Scottcjn/rustchain-bounties/issues/14474",
    # agent playground (helpers)
    "https://github.com/xevrion-v2/agent-playground/issues/3304",
    "https://github.com/xevrion-v2/agent-playground/issues/3258",
    "https://github.com/xevrion-v2/agent-playground/issues/2817",
    # easypeasy/cheapest
    "https://github.com/jessedaustin93/Open-Aeon/issues/1",
    "https://github.com/Markp1598M/Helm/issues/1",
    "https://github.com/Eaprime1/custos/issues/187",
    # walletbeat
    "https://github.com/walletbeat/walletbeat/issues/865",
]

# For each, fetch issue + linked PRs
for u in targets:
    repo_path = "/".join(u.split("/")[3:5])
    n = u.rsplit("/",1)[-1]
    print(f"\n{'='*80}\n{u}\n{'='*80}")
    r = subprocess.run(["gh","pr","list","--repo",repo_path,"--state","all","--search",f"in:body {n}",
                        "--json","number,title,state,createdAt,author,comments"],
                       capture_output=True, text=True, encoding='utf-8', timeout=20)
    if r.returncode == 0:
        try:
            prs = json.loads(r.stdout)
            print(f"PRs referencing this issue: {len(prs)}")
            for p in prs[:5]:
                print(f"  {p['state']:<7}  {p['createdAt'][:10]}  #{p['number']:<5}  @{p['author']['login']:<20}  {p['title'][:60]}")
        except: pass
    # Also fetch issue details (comments count)
    r2 = subprocess.run(["gh","issue","view",u,"--json","comments,labels,title,body,state"],
                        capture_output=True, text=True, encoding='utf-8', timeout=20)
    if r2.returncode == 0:
        d = json.loads(r2.stdout)
        print(f"Issue: {d.get('title','')[:80]}")
        print(f"  state={d.get('state','')}  comments={len(d.get('comments',[]))}  labels={[l['name'] for l in d.get('labels',[])]}")
        body = d.get('body','') or ''
        # Find currency
        for marker in ['XLM','XTM','USDC','USD','XP','RTC']:
            if marker in body:
                import re
                m = re.findall(r'(\d[\d,]*)\s*' + marker, body)
                if m: print(f"  rewards found: {m[0]} {marker}")
                break
