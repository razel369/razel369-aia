import websocket, json
import time

# Connect to debug Chrome
ws = websocket.create_connection("ws://localhost:9222/devtools/browser/3c7e06b3-4ed8-4347-9cca-5fdc63ff98f1", timeout=20)
print("Connected to Chrome")

# Get tabs
ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
print("Targets:", ws.recv()[:300])

# List tabs to find one
ws.send(json.dumps({"id": 2, "method": "Target.getTargets", "params": {"type": "page"}}))
resp = json.loads(ws.recv())
for t in resp.get("result", {}).get("targetInfos", []):
    print(f"  Tab: {t.get('id')[:8]}...  {t.get('url')}  {t.get('type')}")
