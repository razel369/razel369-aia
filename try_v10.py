#!/usr/bin/env python3
"""Find which long value breaks the parser."""
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

# Add long values one at a time
def make_test(long_field=None, long_value="X"*200):
    obs = {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"x","audience":"x","why_allowed_in_venue":"x"}
    if long_field:
        obs[long_field] = long_value
    return {
        "summary": "Field review of runx by AIA, an autonomous insight agent. Posted as a public GitHub issue on razel369/razel369-aia with the full review also stored in docs/runx-review.md.",
        "observations": [obs, dict(obs), dict(obs), dict(obs)]
    }

tests = {
    "v10a_long_summary": make_test("summary", "X"*200),
    "v10b_long_audience": make_test("audience", "X"*200),
    "v10c_long_wav": make_test("why_allowed_in_venue", "X"*200),
    "v10d_long_pturl": make_test("public_url", "https://example.com/" + "X"*200),
    "v10e_all_long": {
        "summary": "X"*200,
        "observations": [
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"X"*200,"audience":"X"*200,"why_allowed_in_venue":"X"*200},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"X"*200,"audience":"X"*200,"why_allowed_in_venue":"X"*200},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"X"*200,"audience":"X"*200,"why_allowed_in_venue":"X"*200},
            {"claim_type":"github_issue_with_review","public_url":"https://github.com/razel369/razel369-aia/issues/1","runx_link_found":True,"summary":"X"*200,"audience":"X"*200,"why_allowed_in_venue":"X"*200}
        ]
    }
}

repo_dir = r"C:\Users\rmalk\projects\razel369-aia"
for name, ev in tests.items():
    path = rf"{repo_dir}\docs\test_{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ev, f, indent=2)
subprocess.run(["git","add","docs/"], capture_output=True, text=True, cwd=repo_dir)
subprocess.run(["git","commit","-m","v10 - field length tests"], capture_output=True, text=True, cwd=repo_dir)
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
