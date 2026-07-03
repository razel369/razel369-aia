#!/usr/bin/env python3
"""Verify the employees.yaml entry passes registration bot validation."""
import yaml, sys

# Simulate what registration.py does
REQUIRED_FIELDS = ("username", "job_title", "address")

with open(r"C:\Users\rmalk\projects\AgentPipe\employees.yaml", encoding="utf-8") as fh:
    data = yaml.safe_load(fh)
print(f"Parsed {len(data.get('employees', []))} employees")
my_entry = [e for e in data.get("employees", []) if e.get("username") == "razel369"]
if not my_entry:
    print("ERROR: razel369 entry not found")
    sys.exit(1)
my_entry = my_entry[0]
print(f"Entry: {my_entry}")

errors = []
extra_keys = set(my_entry) - set(REQUIRED_FIELDS)
if extra_keys:
    errors.append(f"Unexpected fields: {extra_keys}")
for field in REQUIRED_FIELDS:
    value = my_entry.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"Field `{field}` is missing or empty")
if errors:
    print(f"FAIL: {errors}")
    sys.exit(1)
print("PASS: All fields valid")
