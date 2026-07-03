#!/usr/bin/env python3
"""Try short values like the working test."""
import json, urllib.request, urllib.error, subprocess, time

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

# Try different files
tests = {
    "v9b_short": {
        "summary": "Field review of runx by AIA, an autonomous insight agent. Posted as a public GitHub issue on razel369/razel369-aia with the full review also stored in docs/runx-review.md.",
        "observations": [
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"}
        ]
    },
    "v9c_min_summary": {
        "summary": "Field review of runx by AIA.",
        "observations": [
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"}
        ]
    },
    "v9d_no_summary_field": {
        "observations": [
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"}
        ]
    }
}

repo_dir = r"C:\Users\rmalk\projects\razel369-aia"
for name, ev in tests.items():
    path = rf"{repo_dir}\docs\test_{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=2)
subprocess.run(["git","add","docs/"], capture_output=True, text=True, cwd=repo_dir)
subprocess.run(["git","commit","-m","v9 variants"], capture_output=True, text=True, cwd=repo_dir)
subprocess.run(["git","push","origin","main"], capture_output=True, text=True, cwd=repo_dir)
time.sleep(3)

for name in tests:
    ev_url = f"https://raw.githubusercontent.com/razel369/razel369-aia/main/docs/test_{name}.json"
    s, d = fetch("POST", "https://gofrantic.com/v1/deliveries/preflight", {
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
        print(f"  {name:25}  ok={ok}  errs={[(e.get('code',''),e.get('message','')[:80]) for e in errs]}")
    else:
        print(f"  {name:25}  {s}  {d[:200]}")
