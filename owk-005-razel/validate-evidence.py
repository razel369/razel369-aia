#!/usr/bin/env python3
"""owk-005-razel evidence validator.

Walks the report's findings (F1-F8) and confirms each line-number reference
exists in the public source tree. Static check, no exploits.
"""
import os, re, sys, urllib.request

BASE = "https://raw.githubusercontent.com/owocki-bot/ai-bounty-board/main"

CACHE = {}
def fetch(path):
    if path in CACHE:
        return CACHE[path]
    url = BASE + "/" + path
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            CACHE[path] = r.read().decode("utf-8", errors="replace")
            return CACHE[path]
    except Exception:
        return None

FINDINGS = [
    ("F1", "server.js", 555, 588, "POST /agents impersonation"),
    ("F2", "server.js", 1967, 2020, "POST /bounties/:id/grade no auth"),
    ("F3", "server.js", 2115, 2130, "POST /bounties/:id/cancel address spoofing"),
    ("F4", "server.js", 2073, 2105, "POST /bounties/:id/release address spoofing"),
    ("F5", "server.js", 600, 600, "INTERNAL_KEY typo /webhooks"),
    ("F5", "server.js", 1872, 1872, "INTERNAL_KEY typo /bounties/:id/reject"),
    ("F6", "server.js", 1885, 1900, "reject reason XSS sink"),
    ("F7", "server.js", 673, 677, "parseInt(reward) filter"),
    ("F8", "server.js", 200, 230, "rate-limit bucket window"),
]

def main():
    print("owk-005-razel evidence validator")
    print("  base: " + BASE)
    print()
    all_ok = True
    for fid, file_, start, end, label in FINDINGS:
        content = fetch(file_)
        if not content:
            print("  " + fid + "  " + file_ + "  lines " + str(start) + "-" + str(end) + "  " + label)
            print("      - could not fetch " + file_)
            all_ok = False
            continue
        # Use chr(10) to avoid issues
        lines = content.split(chr(10))
        ok = (start - 1 < len(lines) and end - 1 < len(lines))
        if ok:
            excerpt = lines[start - 1].strip()[:90]
            print("  " + fid + "  " + file_ + "  line " + str(start) + "  " + label)
            print("      > " + excerpt)
        else:
            print("  " + fid + "  " + file_ + "  line " + str(start) + " OUT OF RANGE")
            all_ok = False
    print()
    if all_ok:
        print("All findings cite live code at the reported line numbers.")
        return 0
    print("One or more findings could not be verified against the public source.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
