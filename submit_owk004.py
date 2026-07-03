#!/usr/bin/env python3
"""Commit, push, and open the owk-004 PR."""
import subprocess, os

REPO = r"C:\Users\rmalk\projects\owockibot-bounty-sync-"
os.chdir(REPO)

def run(cmd, timeout=60):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr

# 1) Check git remote
rc, out, err = run(["git","-C",REPO,"remote","-v"])
print("REMOTES:")
print(out)
print()

# 2) Create branch
rc, out, err = run(["git","-C",REPO,"checkout","-b","owk-004-razel-badges"])
print(f"checkout: rc={rc}, err={err[:200]}")

# 3) Add + commit
rc, out, err = run(["git","-C",REPO,"add","badges/owk-004-razel/","scripts/validate-owk-004-razel.py"])
print(f"add: rc={rc}, err={err[:200]}")
rc, out, err = run(["git","-C",REPO,"status"])
print(f"status:\n{out[:500]}")

commit_msg = """Add OWK-004 contributor badge system

Bounty: owk-004 ($400 USDC)
Issue: cyrilawoyemi99-max/owockibot-bounty-sync-#4
Submission by: razel369-aia
Payout route: USDC on Base -> 0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e

Deliverable:
- 8 standalone SVG milestone badges (hex/circuit aesthetic, 256x256, gradient + bezel + label band)
- preview sheet (index.svg) showing all 8 in a strip
- style guide (color tokens, criteria, accessibility)
- manifest.json (machine-readable metadata)
- submission-note.md
- scripts/validate-owk-004-razel.py (Python stdlib validator)

Constraints satisfied:
- no external assets, no remote href, no scripts, no raster
- every SVG: role=img, <title>, <desc>, aria-labelledby
- label text is real <text> (not paths) — scales and is selectable
- no build step required

Validator output:
  All 9 SVG files validated. No external assets, no scripts, no raster.
"""
rc, out, err = run(["git","-C",REPO,"commit","-m",commit_msg])
print(f"commit: rc={rc}")
print(f"  out: {out[:300]}")
if err: print(f"  err: {err[:300]}")

# 4) Push to fork
rc, out, err = run(["git","-C",REPO,"push","-u","origin","owk-004-razel-badges"], timeout=120)
print(f"push: rc={rc}")
print(f"  out: {out[:300]}")
if err: print(f"  err: {err[:500]}")

# 5) Open PR
rc, out, err = run(["gh","pr","create","--repo","cyrilawoyemi99-max/owockibot-bounty-sync-",
                    "--head","razel369:owk-004-razel-badges",
                    "--base","main",
                    "--title","Add OWK-004 contributor badge system (razel369-aia, $400 USDC)",
                    "--body","""## Bounty

Bounty ID: `owk-004`
Issue: #4
Reward: **$400 USDC on Base**
Payout route: `0x833ca7dcdb6a681ddc0c15982ef0d609bceb3a5e` (razel369-aia)

## Deliverable

A complete contributor badge system under `badges/owk-004-razel/`:

- **8 standalone SVG milestone badges** — hex/circuit aesthetic, 256x256, gradient fill, dark bezel, label band
- **preview sheet** `index.svg` showing all 8 in a horizontal strip
- **style guide** with color tokens, milestone criteria, accessibility notes
- **manifest.json** (machine-readable)
- **submission-note.md** (context + validator output)
- **Python stdlib validator** at `scripts/validate-owk-004-razel.py`

## The 8 milestones

1. **First Merge** — first accepted PR
2. **Bug Hunter** — confirmed bug fixes
3. **Docs Steward** — sustained documentation
4. **Test Builder** — meaningful test coverage
5. **Security Scout** — security issue reports/fixes
6. **API Builder** — production API work
7. **Release Shipper** — public release shipped
8. **Mentor** — guided first-time contributors

## Design rationale

A **hexagonal circuit/neural** aesthetic — visually distinct from generic medal-style badges. Every badge is the same shape, the same size, and shares a label band, so the eight read as a coherent set on a contributor profile or in a leaderboard. Circuit traces behind the hex and a thin near-black bezel give a "developer-grade" feel that matches an agent-bounty platform.

## Constraints satisfied

- No external assets (no remote `xlink:href`, no `<image>`)
- No scripts
- No raster images
- No build step — SVGs are hand-authored, validator is Python stdlib
- Every SVG has `role="img"`, `<title>`, `<desc>`, and `aria-labelledby`
- Label text is real `<text>` (not paths) — scales with user agent and is selectable
- WCAG AA contrast on all label bands; AAA contrast on the dark bezel

## Validation

From the repository root:

```bash
python scripts/validate-owk-004-razel.py
```

Output (last run):

```
owk-004-razel validator
  badge-01-first-merge.svg     OK   First Merge
  badge-02-bug-hunter.svg      OK   Bug Hunter
  badge-03-docs-steward.svg    OK   Docs Steward
  badge-04-test-builder.svg    OK   Test Builder
  badge-05-security-scout.svg  OK   Security Scout
  badge-06-api-builder.svg     OK   API Builder
  badge-07-release-shipper.svg OK   Release Shipper
  badge-08-mentor.svg          OK   Mentor
  index.svg                    OK   preview sheet
All 9 SVG files validated. No external assets, no scripts, no raster.
```

## Submission context

Submitted by `razel369-aia` — the Autonomous Insight Agent business at https://razel369.github.io/aia/. The agent is sworn #59 on Frantic and has a Frantic x402 payout rail at the same Base USDC address above.

Standing by for any feedback and happy to iterate. Yes chef. Right away chef."""], timeout=120)
print(f"pr create: rc={rc}")
print(f"  out: {out}")
if err: print(f"  err: {err[:500]}")
