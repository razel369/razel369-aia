#!/usr/bin/env python3
"""Strip BOM from post + retry publish."""
import json, urllib.request, urllib.error

with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\devto.key", "rb") as f:
    raw = f.read()
if raw[:3] == b"\xef\xbb\xbf":
    raw = raw[3:]
DEVTO_KEY = raw.decode("utf-8").strip()

def fetch(method, url, data=None, headers=None):
    h = {"User-Agent":"razel369-aia/1.0","Accept":"application/json"}
    if headers: h.update(headers)
    body = None
    if data is not None and not isinstance(data, str):
        h["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
    elif data is not None:
        body = data.encode("utf-8")
    req = urllib.request.Request(url, method=method, data=body, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode("utf-8", errors="replace")
            try:
                return r.status, json.loads(text)
            except:
                return r.status, text
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(text)
        except:
            return e.code, text
    except Exception as e:
        return -1, str(e)

# Read file with explicit BOM-stripping
with open(r"C:\Users\rmalk\projects\razel369-aia\runx_love_post.md", "rb") as f:
    raw = f.read()
# Strip BOM
if raw[:3] == b"\xef\xbb\xbf":
    raw = raw[3:]
content = raw.decode("utf-8")
# Also strip any embedded \ufeff
content = content.replace("\ufeff", "")

# Parse front matter
fm = {}
body_text = content
if content.startswith("---"):
    parts = content.split("---", 2)
    if len(parts) >= 3:
        fm_text = parts[1].strip()
        body_text = parts[2].strip()
        for line in fm_text.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")

print(f"title: {fm.get('title')}")
print(f"body length: {len(body_text)}")
print(f"body first 100: {body_text[:100]}")

article = {
    "article": {
        "title": fm.get("title", "runx field review"),
        "published": True,
        "body_markdown": body_text,
        "description": fm.get("description", ""),
        "canonical_url": fm.get("canonical_url", "https://github.com/runxhq/runx"),
    }
}
tags_str = fm.get("tags", "")
tags = [t.strip() for t in tags_str.replace("[","").replace("]","").replace("'","").replace('"','').split(",") if t.strip()]
article["article"]["tags"] = tags[:4]
print(f"tags: {article['article']['tags']}")

# Use ascii-safe json (no ensure_ascii=False)
s, d = fetch("POST", "https://dev.to/api/articles", article, {"api-key": DEVTO_KEY})
print(f"\nstatus: {s}")
if isinstance(d, dict):
    print(json.dumps(d, indent=2)[:1500])
    post_url = d.get("url")
    post_id = d.get("id")
    if post_url:
        print(f"\nPOST URL: {post_url}")
        print(f"POST ID: {post_id}")
        with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\devto_post.json","w") as f:
            json.dump({"url":post_url,"id":post_id,"title":fm.get("title")}, f, indent=2)
else:
    print(d[:1500])
