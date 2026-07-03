#!/usr/bin/env python3
"""Download Algora JS bundle + extract API endpoints."""
import urllib.request, re, time

url = 'https://console.algora.io/assets/app-5b2057c85821c6362846ca54ef14e54a.js?vsn=d'
req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read().decode('utf-8', errors='replace')
        print(f'size: {len(body)}')
        with open('algora_console.js', 'w', encoding='utf-8') as f:
            f.write(body)
except Exception as e:
    print(f'err: {e}')

# Find fetch URLs
with open('algora_console.js', encoding='utf-8') as f:
    body = f.read()

# Find /api/, /v1/, /graphql paths
seen = set()
for m in re.finditer(r'[\"\'`](/[a-zA-Z][^\"\'`]*)[\"\'`]', body):
    u = m.group(1)
    if any(kw in u for kw in ['api','bount','graphql','trpc','v1/','/v1','query','session','search']) and u not in seen:
        if len(u) < 200 and '://' not in u:
            seen.add(u)
            print(f'  {u}')

# Also find domain names (https://...)
print()
print('Domains:')
for m in re.finditer(r'https?://[a-zA-Z0-9.-]+\.[a-z]{2,}[^\s"\'`]*', body):
    u = m.group(0).rstrip('/')
    if 'github.com' not in u and 'googleapis' not in u and 'jsdelivr' not in u and 'plausible' not in u and 'storageapi' not in u and 'algora.io/storage' not in u and 'avatars' not in u and 'devicon' not in u:
        print(f'  {u[:150]}')
