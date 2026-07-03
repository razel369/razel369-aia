#!/usr/bin/env python3
"""Inspect Open-Aeon repo + claim + build + submit the test bounty."""
import subprocess, json, sys, os, time

# 1) Inspect Open-Aeon
print("=" * 60)
print("Open-Aeon repo")
print("=" * 60)
r = subprocess.run(["gh","repo","view","jessedaustin93/Open-Aeon","--json",
                    "name,description,url,stargazerCount,createdAt,pushedAt,primaryLanguage"],
                   capture_output=True, text=True, encoding='utf-8', timeout=20)
if r.returncode == 0:
    d = json.loads(r.stdout)
    print(json.dumps(d, indent=2))
else:
    print("err:", r.stderr[:300])

print()
print("Open-Aeon contents:")
r = subprocess.run(["gh","api","repos/jessedaustin93/Open-Aeon/contents/"],
                   capture_output=True, text=True, encoding='utf-8', timeout=20)
if r.returncode == 0:
    d = json.loads(r.stdout)
    if isinstance(d, list):
        for f in d[:30]:
            t = f.get("type","?")
            n = f.get("name","")
            s = f.get("size",0)
            print(f"  {t:<5}  {n[:50]:<50}  {s} bytes")
    else:
        print("not a list:", d)
else:
    print("err:", r.stderr[:300])

# 2) Check the issue body for exact requirements
print()
print("Open-Aeon issue #1 body:")
r = subprocess.run(["gh","issue","view","https://github.com/jessedaustin93/Open-Aeon/issues/1",
                    "--json","title,body,labels,state,comments"],
                   capture_output=True, text=True, encoding='utf-8', timeout=20)
if r.returncode == 0:
    d = json.loads(r.stdout)
    print(f"Title: {d.get('title','')}")
    print(f"Labels: {[l['name'] for l in d.get('labels',[])]}")
    print(f"State: {d.get('state','')}  Comments: {len(d.get('comments',[]))}")
    print("Body:")
    print(d.get('body',''))
else:
    print("err:", r.stderr[:300])

# 3) Check the README
print()
print("Open-Aeon README.md:")
r = subprocess.run(["gh","api","repos/jessedaustin93/Open-Aeon/readme"],
                   capture_output=True, text=True, encoding='utf-8', timeout=20)
if r.returncode == 0:
    d = json.loads(r.stdout)
    content = d.get("content","")
    if content:
        import base64
        try:
            text = base64.b64decode(content).decode("utf-8", errors="replace")
            print(text[:3000])
        except Exception as e:
            print("decode err:", e)
    else:
        print("(no content)")
else:
    print("err:", r.stderr[:200])
