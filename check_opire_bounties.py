"""Look at small Opire bounties I can solve in 30-60 min."""
import urllib.request, json, re

ctx = None
HEADERS = {"User-Agent": "razel369-aia/1.0"}

# Featured bounties from opire.dev
ISSUES = [
    ("01J8T24PJDXX69RM7XV24SQT11", "qtop $70 test coverage", "Python", 2),
    ("01HWT2MKE4GWPJXDPMAFEAHHHE", "QueryEngine $30 deleteMany", "TypeScript", 2),
    ("01HWT26R3S59MS778MAE9786YG", "storybook $263 controls select", "TypeScript", 4),
    ("01J6HJZCK02FVD4XG900FY36EE", "zed $345 helix keymap", "Rust", 5),
    ("01J73BXYSGA83XKW25TPF2QMK0", "autokey $590 wayland", "Python", 24),
    ("01HWJNZ5HQMVG2TCW6XHQQJ3QT", "typeorm $590 migration", "TypeScript", 24),
]

for slug, name, lang, solvers in ISSUES:
    print(f"\n=== {name} (lang={lang}, solvers={solvers}) ===")
    try:
        url = f"https://r.jina.ai/https://app.opire.dev/issues/{slug}"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            content = r.read().decode()
        # Extract key info
        title_match = re.search(r'Title:\s*(.+)', content)
        if title_match:
            print(f"  Title: {title_match.group(1)}")
        # Get body excerpt
        body_start = content.find('Markdown Content:')
        if body_start > 0:
            body = content[body_start:body_start+2500]
            print(f"  Body: {body[:2500]}")
    except Exception as e:
        print(f"  ERR: {e}")
