#!/usr/bin/env python3
"""Try simpler evidence structures to find what works."""
import json, urllib.request, urllib.error, subprocess

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

# Multiple candidate structures
candidates = {
    "v1_simple_array": {
        "observations": [
            "claim_type=github_issue_with_review",
            "public_url=https://github.com/razel369/razel369-aia/issues/1",
            "runx_link_found=true",
            "summary=Field review of runx by AIA, an autonomous insight agent. Posted as a public GitHub issue with the full review also stored in docs/runx-review.md.",
            "audience=Agent operators building paid/autonomous agents on x402.",
            "why_allowed_in_venue=GitHub issues are a public, accepted venue for technical reviews, project discussions, and contributions."
        ]
    },
    "v2_string_objects": {
        "observations": [
            {"text":"claim_type=github_issue_with_review"},
            {"text":"public_url=https://github.com/razel369/razel369-aia/issues/1"},
            {"text":"runx_link_found=true"},
            {"text":"summary=Field review of runx by AIA"},
            {"text":"audience=Agent operators"},
            {"text":"why_allowed_in_venue=GitHub issues are public"}
        ]
    },
    "v3_items_key": {
        "items": [
            {"claim_type":"github_issue_with_review"},
            {"public_url":"https://github.com/razel369/razel369-aia/issues/1"},
            {"runx_link_found":True},
            {"summary":"Field review of runx by AIA"},
            {"audience":"Agent operators"},
            {"why_allowed_in_venue":"GitHub issues are public"}
        ]
    },
    "v4_data_observations": {
        "data": {
            "observations": [
                {"claim_type":"github_issue_with_review"},
                {"public_url":"https://github.com/razel369/razel369-aia/issues/1"},
                {"runx_link_found":True},
                {"summary":"Field review"},
                {"audience":"Operators"},
                {"why_allowed_in_venue":"Public"}
            ]
        }
    },
    "v5_named_keys": {
        "observations": [
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"Field review","audience":"Operators","why_allowed_in_venue":"Public"}
        ]
    },
    "v6_just_list": [
        {"claim_type":"github_issue_with_review"},
        {"public_url":"https://github.com/razel369/razel369-aia/issues/1"},
        {"runx_link_found":True},
        {"summary":"Field review of runx"},
        {"audience":"Operators"},
        {"why_allowed_in_venue":"Public"}
    ]
}

# Save each + preflight
import time
repo_dir = r"C:\Users\rmalk\projects\razel369-aia"
for name, ev in candidates.items():
    path = rf"{repo_dir}\docs\evidence_test_{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=2)
    subprocess.run(["git","add",f"docs/evidence_test_{name}.json"], capture_output=True, text=True, cwd=repo_dir)
subprocess.run(["git","commit","-m","Test evidence structures for Frantic #49"], capture_output=True, text=True, cwd=repo_dir)
subprocess.run(["git","push","origin","main"], capture_output=True, text=True, cwd=repo_dir)
time.sleep(2)

preflight_url = "https://gofrantic.com/v1/deliveries/preflight"
for name, ev in candidates.items():
    ev_url = f"https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/evidence_test_{name}.json"
    s, d = fetch("POST", preflight_url, {
        "bounty":"49",
        "artifact_refs":[
            f"public_url=https://github.com/razel369/razel369-aia/issues/1",
            f"evidence_json={ev_url}",
            f"report=https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/runx_love_report.md"
        ]
    })
    if isinstance(d, dict):
        pre = d.get("preflight", d)
        ok = pre.get("ok", False)
        errs = pre.get("errors", [])
        print(f"  {name:30}  ok={ok}  errs={[e.get('code','') for e in errs]}")
        for e in errs:
            print(f"     {e.get('message','')[:120]}")
    else:
        print(f"  {name:30}  {s}  {d[:200]}")
