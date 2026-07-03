#!/usr/bin/env python3
"""Write clean key (no BOM) + republish."""
key = "Dg5DQxCQcqPEj5D9R6Ax9yic1jo7grB2cwSdNKBE94dU2pNeK4gKQDPJ"
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\devto.key", "wb") as f:
    f.write(key.encode("utf-8"))
print(f"wrote {len(key)} chars")
# Verify
with open(r"C:\Users\rmalk\projects\razel369-aia\.agent-credentials\devto.key", "rb") as f:
    raw = f.read()
print(f"first 5 bytes: {raw[:5]}")
print(f"has BOM: {raw[:3] == b'\\xef\\xbb\\xbf'}")
