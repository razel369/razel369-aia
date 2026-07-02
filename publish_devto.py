"""Cross-post the AIA launch post to dev.to via API.
Setup: set DEVTO_API_KEY in env (https://dev.to/settings/extensions).
"""
import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

API = "https://dev.to/api/articles"
POST_PATH = Path(__file__).parent / "launch_post.md"

def _read_post():
    text = POST_PATH.read_text(encoding="utf-8-sig")
    # Split frontmatter
    if not text.lstrip().startswith("---"):
        return None, text
    end = text.find("---", 3)
    if end == -1:
        return None, text
    fm = text[3:end].strip()
    body = text[end+3:].strip()
    meta = {}
    for line in fm.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body

def main(dry_run=False):
    try:
        from agent import config as _cfg
        api_key = _cfg.DEVTO_API_KEY
    except Exception:
        api_key = ""
    api_key = api_key or os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print("DEVTO_API_KEY not set — skipping dev.to cross-post.")
        print("Set it with:  $env:DEVTO_API_KEY = 'your-key'")
        return False
    meta, body = _read_post()
    if not meta or not body:
        print("Post parse failed")
        return False
    payload = {
        "article": {
            "title": meta.get("title", "AIA — Autonomous Insight Agent"),
            "published": str(meta.get("published", "true")).lower() == "true",
            "body_markdown": body,
            "tags": [t.strip() for t in meta.get("tags", "ai,opensource,agents,web3").split(",")][:4],
            "canonical_url": meta.get("canonical_url", ""),
            "description": meta.get("description", ""),
        }
    }
    if dry_run:
        print(json.dumps(payload, indent=2)[:2000])
        return True
    req = urllib.request.Request(
        API,
        data=json.dumps(payload).encode("utf-8"),
        headers={"api-key": api_key, "Content-Type": "application/json",
                 "User-Agent": "AIA-Agent/0.1", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
            print("Published:", data.get("url"))
            return True
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:500]}")
        return False

if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
