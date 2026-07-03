#!/usr/bin/env python3
"""Build the Python validator for owk-004 badges."""
import os, xml.etree.ElementTree as ET

SCRIPT = '''#!/usr/bin/env python3
"""owk-004-razel validator.

Verifies every SVG under badges/owk-004-razel/ satisfies the owk-004 constraints:
- well-formed XML
- declares role="img" with <title> and <desc> and aria-labelledby
- no <script>
- no <image> with remote href
- no xlink:href to remote URLs
- no embedded raster (data:image/png, data:image/jpeg)
- standalone (no <foreignObject>)
"""
import os, re, sys, xml.etree.ElementTree as ET

BADGE_DIR = os.path.join(os.path.dirname(__file__), "..", "badges", "owk-004-razel")
BADGE_DIR = os.path.normpath(BADGE_DIR)

EXPECTED = [
    ("badge-01-first-merge.svg",    "First Merge"),
    ("badge-02-bug-hunter.svg",     "Bug Hunter"),
    ("badge-03-docs-steward.svg",   "Docs Steward"),
    ("badge-04-test-builder.svg",   "Test Builder"),
    ("badge-05-security-scout.svg", "Security Scout"),
    ("badge-06-api-builder.svg",    "API Builder"),
    ("badge-07-release-shipper.svg","Release Shipper"),
    ("badge-08-mentor.svg",         "Mentor"),
    ("index.svg",                   "preview sheet"),
]

REMOTE_HREF = re.compile(r"^https?://", re.IGNORECASE)
DATA_IMAGE  = re.compile(r"^data:image/(png|jpeg|jpg|gif|webp)", re.IGNORECASE)

def validate(path, label):
    issues = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return False, [f"XML parse error: {e}"]
    root = tree.getroot()
    ns = "{http://www.w3.org/2000/svg}"
    if not root.tag.endswith("svg"):
        issues.append(f"root is {root.tag}, not svg")
    if root.get("role") != "img":
        issues.append('missing role="img"')
    if not root.get("aria-labelledby"):
        issues.append("missing aria-labelledby")
    title = root.find(f"{ns}title")
    desc  = root.find(f"{ns}desc")
    if title is None: issues.append("missing <title>")
    if desc  is None: issues.append("missing <desc>")
    for s in root.iter(f"{ns}script"):
        issues.append("contains <script>")
    for f in root.iter(f"{ns}foreignObject"):
        issues.append("contains <foreignObject>")
    for img in root.iter(f"{ns}image"):
        href = img.get("href") or img.get("{http://www.w3.org/1999/xlink}href") or ""
        if REMOTE_HREF.match(href) or DATA_IMAGE.match(href):
            issues.append(f"remote/raster image: {href[:60]}")
    for el in root.iter():
        for attr in ("href","{http://www.w3.org/1999/xlink}href"):
            v = el.get(attr)
            if v and REMOTE_HREF.match(v):
                issues.append(f"remote href in {el.tag}: {v[:60]}")
    return (len(issues) == 0), issues

def main():
    print("owk-004-razel validator")
    print(f"  scanning {BADGE_DIR}")
    print()
    all_ok = True
    for fname, label in EXPECTED:
        path = os.path.join(BADGE_DIR, fname)
        if not os.path.exists(path):
            print(f"  {fname:34s} MISSING")
            all_ok = False
            continue
        ok, issues = validate(path, label)
        if ok:
            print(f"  {fname:34s} OK   {label}")
        else:
            all_ok = False
            print(f"  {fname:34s} FAIL {label}")
            for i in issues:
                print(f"      - {i}")
    print()
    if all_ok:
        print(f"All {len(EXPECTED)} SVG files validated. No external assets, no scripts, no raster.")
        return 0
    print("Validation FAILED.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
'''

# Create scripts dir and write
scripts_dir = r"C:\Users\rmalk\projects\owockibot-bounty-sync-\scripts"
os.makedirs(scripts_dir, exist_ok=True)
script_path = os.path.join(scripts_dir, "validate-owk-004-razel.py")
with open(script_path, "w", encoding="utf-8") as f:
    f.write(SCRIPT)
print(f"wrote {script_path}")

# Run the validator
import subprocess
r = subprocess.run(["python","-X","utf8",script_path], capture_output=True, text=True, timeout=30)
print()
print("VALIDATOR OUTPUT:")
print(r.stdout)
if r.stderr:
    print("STDERR:", r.stderr)
print(f"return: {r.returncode}")
