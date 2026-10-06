#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/CODEPATH-BINDINGS.json"

def main():
    if not REPORT.exists():
        print("FAIL: CODEPATH-BINDINGS.json missing")
        return 1
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    total = data.get("binding_count", 0)
    bound = data.get("bound", 0)
    print("WVP Codepath Binding Check")
    print("Bound:", f"{bound}/{total}")
    if total == 0:
        print("FAIL: no bindings defined")
        return 1
    if bound < total:
        print("WARN: some fixtures are unbound")
        return 0
    print("PASS: all fixtures have at least one codepath binding")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
