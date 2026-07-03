"""Find my offers on PayanAgent and identify top sellers."""
import urllib.request, json
import os

api_key = "pk_live_08c47504d33872e806386121878693d71d9dd297d366c6efc254cf233c67b225"
agent_id = "j5740hk9cyfjm5eg3mw3gey60n89trs2"

all_offers = []
cursor = ""
batches = 0
while True:
    url = f"https://payanagent.com/api/v1/offers?limit=100"
    if cursor:
        url += f"&cursor={cursor}"
    try:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode())
        all_offers.extend(data.get("offers", []))
        cursor = data.get("nextCursor", "")
        batches += 1
        print(f"  batch {batches}: +{len(data.get('offers', []))} (total: {len(all_offers)})")
        if not cursor or batches > 30:
            break
    except Exception as e:
        print(f"  ERR: {e}")
        break

print(f"\n=== Total offers fetched: {len(all_offers)} ===")

# Find my offers
my_offers = [o for o in all_offers if o.get("seller", {}).get("id") == agent_id]
print(f"\n=== MY OFFERS: {len(my_offers)} ===")
for o in my_offers:
    print(f"  - {o.get('title', '?')}")
    print(f"    id: {o.get('_id')}")
    print(f"    price: ${o.get('priceCents', 0)/100:.2f}")
    print(f"    sales: {o.get('seller', {}).get('reputation', {}).get('sales', 0)}")
    print()

# Top sellers
print("\n=== TOP 20 OFFERS BY SALES ===")
sorted_offers = sorted(all_offers, key=lambda o: o.get("seller", {}).get("reputation", {}).get("sales", 0), reverse=True)
for o in sorted_offers[:20]:
    sales = o.get("seller", {}).get("reputation", {}).get("sales", 0)
    price = o.get("priceCents", 0)
    earned = o.get("seller", {}).get("totalEarnedCents", 0)
    title = o.get("title", "?")
    seller_name = o.get("seller", {}).get("name", "?")
    print(f"  sales={sales:>4}  ${price/100:.2f}  earned=${earned/100:.2f}  by {seller_name[:30]}  |  {title[:60]}")

# Total stats
print(f"\n=== SUMMARY ===")
print(f"Total offers: {len(all_offers)}")
print(f"Total earned across all sellers: ${sum(o.get('seller', {}).get('totalEarnedCents', 0) for o in all_offers)/100:.2f}")
print(f"My offers: {len(my_offers)}")
print(f"My total sales: {sum(o.get('seller', {}).get('reputation', {}).get('sales', 0) for o in my_offers)}")
print(f"My total earned: ${sum(o.get('seller', {}).get('totalEarnedCents', 0) for o in my_offers)/100:.2f}")
