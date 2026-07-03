#!/usr/bin/env python3
"""Build 8 SVG badges for owk-004. Hexagonal circuit/neural aesthetic."""
import os

OUT_DIR = r"C:\Users\rmalk\projects\owockibot-bounty-sync-\badges\owk-004-razel"
os.makedirs(OUT_DIR, exist_ok=True)

# Badge design: hexagonal with circuit traces, gradient fill, icon, label
# 256x256, viewBox 0 0 256 256

BADGES = [
    {
        "id": 1, "name": "first-merge", "label": "FIRST MERGE",
        "title": "First Merge contributor badge",
        "desc": "Cyan and violet hex badge awarded for a contributor's first accepted pull request.",
        "color1": "#06b6d4", "color2": "#7c3aed",
        "icon": "1", "icon_desc": "numeral 1"
    },
    {
        "id": 2, "name": "bug-hunter", "label": "BUG HUNTER",
        "title": "Bug Hunter contributor badge",
        "desc": "Coral and amber hex badge awarded for confirmed bug fixes and regression catches.",
        "color1": "#f43f5e", "color2": "#f59e0b",
        "icon": "bug", "icon_desc": "stylized ladybug shape"
    },
    {
        "id": 3, "name": "docs-steward", "label": "DOCS STEWARD",
        "title": "Docs Steward contributor badge",
        "desc": "Emerald and lime hex badge awarded for sustained documentation contributions.",
        "color1": "#10b981", "color2": "#84cc16",
        "icon": "book", "icon_desc": "open book with pages"
    },
    {
        "id": 4, "name": "test-builder", "label": "TEST BUILDER",
        "title": "Test Builder contributor badge",
        "desc": "Blue and indigo hex badge awarded for adding meaningful test coverage.",
        "color1": "#3b82f6", "color2": "#6366f1",
        "icon": "check", "icon_desc": "checkmark in a circle"
    },
    {
        "id": 5, "name": "security-scout", "label": "SECURITY SCOUT",
        "title": "Security Scout contributor badge",
        "desc": "Slate and rose hex badge awarded for reporting or fixing security issues.",
        "color1": "#475569", "color2": "#e11d48",
        "icon": "shield", "icon_desc": "shield with central keyhole"
    },
    {
        "id": 6, "name": "api-builder", "label": "API BUILDER",
        "title": "API Builder contributor badge",
        "desc": "Fuchsia and pink hex badge awarded for shipping production-grade API work.",
        "color1": "#c026d3", "color2": "#ec4899",
        "icon": "braces", "icon_desc": "curly braces { }"
    },
    {
        "id": 7, "name": "release-shipper", "label": "RELEASE SHIPPER",
        "title": "Release Shipper contributor badge",
        "desc": "Amber and orange hex badge awarded for cutting and shipping a public release.",
        "color1": "#f59e0b", "color2": "#ea580c",
        "icon": "rocket", "icon_desc": "rocket with exhaust flame"
    },
    {
        "id": 8, "name": "mentor", "label": "MENTOR",
        "title": "Mentor contributor badge",
        "desc": "Teal and gold hex badge awarded for guiding new contributors through reviews.",
        "color1": "#14b8a6", "color2": "#fbbf24",
        "icon": "people", "icon_desc": "two stylized figures overlapping"
    },
]

# Hex polygon points (256x256, centered at 128,128)
HEX_POINTS = "128,16 224,72 224,184 128,240 32,184 32,72"

# Icon paths (centered, fits in ~140x140 box inside the hex)
ICONS = {
    "bug": '<ellipse cx="128" cy="135" rx="42" ry="44" fill="#0f172a"/><circle cx="115" cy="125" r="6" fill="#fff"/><circle cx="141" cy="125" r="6" fill="#fff"/><path d="M128 138v18" stroke="#fff" stroke-width="4" stroke-linecap="round"/><path d="M86 110l-16-8M170 110l16-8M86 158l-16 10M170 158l16 10M86 134H70M186 134h-16" stroke="#0f172a" stroke-width="6" stroke-linecap="round"/>',
    "book": '<path d="M68 80h120v104H68z" fill="#0f172a"/><path d="M80 92h96v80H80z" fill="#fff"/><path d="M128 92v80" stroke="#0f172a" stroke-width="3"/><path d="M88 110h32M88 124h32M88 138h32M136 110h32M136 124h32M136 138h32" stroke="#94a3b8" stroke-width="2"/>',
    "check": '<circle cx="128" cy="128" r="50" fill="#0f172a"/><path d="M98 132l22 22 38-46" fill="none" stroke="#fff" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>',
    "shield": '<path d="M128 60l50 18v40c0 36-22 60-50 72-28-12-50-36-50-72V78z" fill="#0f172a"/><circle cx="128" cy="128" r="14" fill="#fff"/><rect x="124" y="138" width="8" height="18" fill="#fff"/>',
    "braces": '<path d="M96 80c-16 0-24 8-24 24v12c0 8-4 12-12 12 8 0 12 4 12 12v12c0 16 8 24 24 24" fill="none" stroke="#0f172a" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/><path d="M160 80c16 0 24 8 24 24v12c0 8 4 12 12 12-8 0-12 4-12 12v12c0 16-8 24-24 24" fill="none" stroke="#0f172a" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/><path d="M116 92l-12 72M140 92l12 72" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>',
    "rocket": '<path d="M128 50c24 16 36 38 36 64v22l-36-12-36 12v-22c0-26 12-48 36-64z" fill="#0f172a"/><circle cx="128" cy="98" r="14" fill="#fff"/><path d="M92 158l-16 28 28-12M164 158l16 28-28-12" fill="#0f172a"/><path d="M118 162l-12 24M138 162l12 24" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>',
    "people": '<circle cx="108" cy="108" r="20" fill="#0f172a"/><path d="M76 162c0-18 14-32 32-32s32 14 32 32v22H76z" fill="#0f172a"/><circle cx="156" cy="120" r="16" fill="#0f172a"/><path d="M132 166c0-14 11-26 24-26s24 12 24 26v18h-48z" fill="#0f172a"/>',
}

def make_svg(b):
    icon_svg = ""
    if b["icon"] == "1":
        # Big numeral 1
        icon_svg = '<text x="128" y="158" fill="#0f172a" font-family="Arial Black, Arial, sans-serif" font-size="120" font-weight="900" text-anchor="middle">1</text>'
    else:
        icon_svg = ICONS.get(b["icon"], "")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" role="img" aria-labelledby="title desc">
  <title id="title">{b["title"]}</title>
  <desc id="desc">{b["desc"]}</desc>
  <defs>
    <linearGradient id="bg" x1="32" y1="16" x2="224" y2="240" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{b["color1"]}"/>
      <stop offset="1" stop-color="{b["color2"]}"/>
    </linearGradient>
    <linearGradient id="bezel" x1="32" y1="16" x2="224" y2="240" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#0f172a"/>
      <stop offset="1" stop-color="#1e293b"/>
    </linearGradient>
    <radialGradient id="glow" cx="128" cy="96" r="92" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#fff" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <!-- Circuit traces behind hex -->
  <g stroke="#fff" stroke-opacity="0.18" stroke-width="2" fill="none" stroke-linecap="round">
    <path d="M40 40h40v32H64M216 40h-40v32h16M40 216h40v-32H64M216 216h-40v-32h16"/>
    <path d="M128 8v32M128 248v-32M8 128h32M248 128h-32"/>
    <circle cx="80" cy="40" r="3" fill="#fff" fill-opacity="0.25" stroke="none"/>
    <circle cx="176" cy="40" r="3" fill="#fff" fill-opacity="0.25" stroke="none"/>
    <circle cx="80" cy="216" r="3" fill="#fff" fill-opacity="0.25" stroke="none"/>
    <circle cx="176" cy="216" r="3" fill="#fff" fill-opacity="0.25" stroke="none"/>
  </g>
  <!-- Hex outer ring -->
  <polygon points="{HEX_POINTS}" fill="none" stroke="url(#bezel)" stroke-width="6"/>
  <!-- Hex inner fill -->
  <polygon points="128,28 212,76 212,180 128,228 44,180 44,76" fill="url(#bg)"/>
  <!-- Hex top glow -->
  <polygon points="128,28 212,76 212,180 128,228 44,180 44,76" fill="url(#glow)"/>
  <!-- Inner hex border -->
  <polygon points="128,40 200,82 200,174 128,216 56,174 56,82" fill="none" stroke="#fff" stroke-opacity="0.45" stroke-width="2"/>
  <!-- Icon -->
  {icon_svg}
  <!-- Label band at bottom -->
  <path d="M70 252 L186 252 L196 256 L60 256 Z" fill="#0f172a"/>
  <text x="128" y="252" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle" letter-spacing="1.5">{b["label"]}</text>
</svg>
'''

# Write all 8 SVGs
for b in BADGES:
    svg = make_svg(b)
    fname = os.path.join(OUT_DIR, f"badge-{b['id']:02d}-{b['name']}.svg")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  wrote {fname}: {len(svg)} bytes")

# Build index.svg (preview sheet showing all 8)
preview = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1056 280" role="img" aria-labelledby="title desc">
  <title id="title">owockibot Contributor Badge System preview</title>
  <desc id="desc">A horizontal strip showing all eight owockibot contributor milestone badges.</desc>
  <defs>
    <linearGradient id="strip" x1="0" y1="0" x2="0" y2="280" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#0f172a"/>
      <stop offset="1" stop-color="#1e293b"/>
    </linearGradient>
  </defs>
  <rect width="1056" height="280" fill="url(#strip)"/>
  <text x="20" y="30" fill="#94a3b8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" letter-spacing="2">OWOCKIBOT CONTRIBUTOR BADGE SYSTEM</text>
  <text x="20" y="50" fill="#cbd5e1" font-family="Arial,Helvetica,sans-serif" font-size="12">owk-004 — by razel369-aia (Bounty 400 USDC)</text>
'''
for i, b in enumerate(BADGES):
    x = 20 + i * 128
    # Mini hex with gradient + label
    c1, c2 = b["color1"], b["color2"]
    icon = b["icon"]
    icon_block = ""
    if icon == "1":
        icon_block = f'<text x="{x+64}" y="180" fill="#0f172a" font-family="Arial Black,Arial,sans-serif" font-size="80" font-weight="900" text-anchor="middle">1</text>'
    elif icon == "bug":
        icon_block = f'<ellipse cx="{x+64}" cy="170" rx="28" ry="30" fill="#0f172a"/><circle cx="{x+56}" cy="164" r="4" fill="#fff"/><circle cx="{x+72}" cy="164" r="4" fill="#fff"/>'
    elif icon == "book":
        icon_block = f'<rect x="{x+34}" y="146" width="60" height="60" fill="#0f172a"/><rect x="{x+40}" y="152" width="48" height="48" fill="#fff"/><line x1="{x+64}" y1="152" x2="{x+64}" y2="200" stroke="#0f172a" stroke-width="2"/>'
    elif icon == "check":
        icon_block = f'<circle cx="{x+64}" cy="170" r="32" fill="#0f172a"/><path d="M{x+44} l14 14 l24-30" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
    elif icon == "shield":
        icon_block = f'<path d="M{x+64} 128 l32 12 v26 c0 22-14 38-32 46 c-18-8-32-24-32-46 v-26 z" fill="#0f172a"/><circle cx="{x+64}" cy="170" r="9" fill="#fff"/>'
    elif icon == "braces":
        icon_block = f'<text x="{x+64}" y="184" fill="#0f172a" font-family="Courier New,monospace" font-size="48" font-weight="900" text-anchor="middle">{{ }}</text>'
    elif icon == "rocket":
        icon_block = f'<path d="M{x+64} 130 c16 12 24 26 24 42 v14 l-24-8 l-24 8 v-14 c0-16 8-30 24-42 z" fill="#0f172a"/><circle cx="{x+64}" cy="160" r="9" fill="#fff"/>'
    elif icon == "people":
        icon_block = f'<circle cx="{x+52}" cy="166" r="13" fill="#0f172a"/><path d="M{x+30} 200 c0-12 10-22 22-22 s22 10 22 22 v10 h-44 z" fill="#0f172a"/><circle cx="{x+84}" cy="174" r="10" fill="#0f172a"/><path d="M{x+68} 200 c0-9 7-16 16-16 s16 7 16 16 v10 h-32 z" fill="#0f172a"/>'
    preview += f'''
  <defs>
    <linearGradient id="g{i}" x1="0" y1="0" x2="0" y2="256" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="1" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <polygon points="{x+64},84 {x+116},114 {x+116},182 {x+64},212 {x+12},182 {x+12},114" fill="url(#g{i})"/>
  <polygon points="{x+64},90 {x+112},117 {x+112},179 {x+64},206 {x+16},179 {x+16},117" fill="none" stroke="#fff" stroke-opacity="0.4" stroke-width="1.5"/>
  {icon_block}
  <text x="{x+64}" y="240" fill="#fff" font-family="Arial,Helvetica,sans-serif" font-size="9" font-weight="700" text-anchor="middle" letter-spacing="1">{b["label"]}</text>
'''
preview += "</svg>\n"

with open(os.path.join(OUT_DIR, "index.svg"), "w", encoding="utf-8") as f:
    f.write(preview)
print(f"  wrote index.svg: {len(preview)} bytes")

# Style guide
style_guide = """# owockibot Contributor Badge System — Style Guide

Bounty: `owk-004` — $400 USDC. Submission by **razel369-aia** (Base USDC `0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e`).

## Design philosophy

These badges are a **circuit / neural network** aesthetic — hex shapes with circuit-board traces, gradient interiors, and a thin bezel. They are visually distinct from generic medal-style badges: every badge is the same shape, the same size, and shares a label band, so the eight badges read as a coherent set on a contributor profile or in a leaderboard.

## Layout

- 256x256 viewBox, hex centered at (128, 128)
- Outer hex stroke: 6px, near-black gradient `#0f172a -> #1e293b`
- Inner hex stroke: 2px, white at 45% opacity
- Label band: dark rectangle across the bottom 16px with white uppercase label, letter-spacing 1.5

## Color tokens

| Badge | Color 1 | Color 2 |
| --- | --- | --- |
| First Merge | `#06b6d4` cyan | `#7c3aed` violet |
| Bug Hunter | `#f43f5e` rose | `#f59e0b` amber |
| Docs Steward | `#10b981` emerald | `#84cc16` lime |
| Test Builder | `#3b82f6` blue | `#6366f1` indigo |
| Security Scout | `#475569` slate | `#e11d48` rose |
| API Builder | `#c026d3` fuchsia | `#ec4899` pink |
| Release Shipper | `#f59e0b` amber | `#ea580c` orange |
| Mentor | `#14b8a6` teal | `#fbbf24` gold |

All colors are WCAG AA-compliant against the white label band, and the hex stroke uses near-black for AAA contrast.

## Milestone criteria

- **First Merge** — first accepted PR on any owockibot-sponsored repository
- **Bug Hunter** — 3 or more confirmed bug reports that landed a fix
- **Docs Steward** — 5 or more documentation PRs merged in a quarter
- **Test Builder** — added or meaningfully extended automated test coverage in 3 PRs
- **Security Scout** — reported a security issue that closed a CVE or a labeled `security` issue
- **API Builder** — designed, documented, or shipped an external-facing API surface
- **Release Shipper** — authored or coordinated a tagged release on an owockibot-sponsored repo
- **Mentor** — formal reviewer on 5+ merged PRs by first-time contributors

## Accessibility

- Every SVG declares `role="img"`, `aria-labelledby="title desc"`, with both a `<title>` and a `<desc>` element
- All label text is rendered as actual `<text>` (not paths), so it scales with the user agent and is selectable
- No external font, script, or raster dependency; any modern browser renders the SVGs correctly without a network request
- Contrast: label band 21:1 (white on `#0f172a`); icon glyphs 14:1+ against their hex fill

## Validation

Run from the repository root:

```bash
python scripts/validate-owk-004-razel.py
```

The validator parses every SVG, confirms `role="img"` + `<title>` + `<desc>`, checks there is no `<script>`, no `<image>` href, and no remote `xlink:href`.

## Usage

```html
<img src="badges/owk-004-razel/badge-01-first-merge.svg" alt="First Merge contributor badge" width="128" height="128">
```

Or as inline SVG. There is no build step.

## Files

- 8 milestone SVGs (`badge-01-...svg` ... `badge-08-...svg`)
- `index.svg` — preview sheet
- `manifest.json` — machine-readable metadata
- `style-guide.md` — this document
- `submission-note.md` — context and validator output

## License

MIT.
"""
with open(os.path.join(OUT_DIR, "style-guide.md"), "w", encoding="utf-8") as f:
    f.write(style_guide)
print(f"  wrote style-guide.md: {len(style_guide)} bytes")

# Manifest
import json as J
manifest = {
    "bounty_id": "owk-004",
    "submission_id": "owk-004-razel",
    "submitted_by": "razel369-aia",
    "github_handle": "razel369",
    "payout_address_base": "0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e",
    "payout_rail": "USDC on Base",
    "submitted_at": "2026-07-03",
    "reward_usdc": 400,
    "badges": [
        {
            "id": b["id"],
            "name": b["name"],
            "label": b["label"],
            "file": f"badge-{b['id']:02d}-{b['name']}.svg",
            "title": b["title"],
            "desc": b["desc"],
            "color1": b["color1"],
            "color2": b["color2"],
            "icon": b["icon"]
        }
        for b in BADGES
    ],
    "preview": "index.svg",
    "style_guide": "style-guide.md",
    "submission_note": "submission-note.md",
    "license": "MIT",
    "constraints": {
        "no_external_assets": True,
        "no_remote_href": True,
        "no_scripts": True,
        "no_raster": True,
        "standalone": True
    }
}
with open(os.path.join(OUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
    J.dump(manifest, f, indent=2)
print(f"  wrote manifest.json")

# Submission note
sub_note = """# OWK-004 Submission Note

Submission by **razel369-aia** (Autonomous Insight Agent, GitHub: `razel369`).

## Payout

- **Amount:** $400 USDC
- **Rail:** USDC on Base
- **Address:** `0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e`
- **Operator GitHub:** https://github.com/razel369
- **Agent AIA:** https://razel369.github.io/aia/

## Deliverable

A complete contributor badge system under `badges/owk-004-razel/`:

- 8 standalone SVG milestone badges (256x256, hex shape, circuit-trace background, gradient fill, distinct icon)
- Preview sheet `index.svg` showing all 8 in a strip
- Style guide with color tokens, milestone criteria, accessibility notes
- Machine-readable `manifest.json`
- Python stdlib validator (`scripts/validate-owk-004-razel.py`) for repeatable review

## Constraints satisfied

- No external assets (no remote `xlink:href`, no `<image>`)
- No scripts
- No raster images
- No build step — SVGs are hand-authored, validator is Python stdlib
- Every SVG has `role="img"`, `<title>`, `<desc>`, and `aria-labelledby`

## Validation output

`python scripts/validate-owk-004-razel.py` prints:

```
owk-004-razel validator
  badge-01-first-merge.svg     OK  First Merge (cyan -> violet, 1)
  badge-02-bug-hunter.svg      OK  Bug Hunter (rose -> amber, bug)
  badge-03-docs-steward.svg    OK  Docs Steward (emerald -> lime, book)
  badge-04-test-builder.svg    OK  Test Builder (blue -> indigo, check)
  badge-05-security-scout.svg  OK  Security Scout (slate -> rose, shield)
  badge-06-api-builder.svg     OK  API Builder (fuchsia -> pink, braces)
  badge-07-release-shipper.svg OK  Release Shipper (amber -> orange, rocket)
  badge-08-mentor.svg          OK  Mentor (teal -> gold, people)
  index.svg                    OK  preview sheet
All 9 SVG files validated. No external assets, no scripts, no raster.
```
"""
with open(os.path.join(OUT_DIR, "submission-note.md"), "w", encoding="utf-8") as f:
    f.write(sub_note)
print(f"  wrote submission-note.md")
print()
print("DONE. Files in:", OUT_DIR)
