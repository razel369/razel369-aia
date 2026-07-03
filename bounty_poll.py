#!/usr/bin/env python3
"""Continuous bounty poller — finds new $$ bounties every 30 minutes."""
import json, time, subprocess
from datetime import datetime

while True:
    try:
        subprocess.run(["python", "C:\\Users\\rmalk\\projects\\razel369-aia\\bounty_hunt.py"], timeout=300)
    except Exception as e:
        print(f"err: {e}")
    time.sleep(1800)  # 30 min
