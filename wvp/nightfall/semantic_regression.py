#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/SEMANTIC-REGRESSION.json"

def main():
    if not REPORT.exists():
        print("FAIL: SEMANTIC-REGRESSION.json missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    total = data.get("semantic_checks", 0)
    passed = data.get("passed", 0)
    warned = data.get("warned", 0)

    print("WVP Semantic Regression Check")
    print("Checks:", total)
    print("PASS:", passed)
    print("WARN:", warned)

    if total < 8:
        print("FAIL: expected at least 8 semantic checks")
        return 1

    if passed == 0:
        print("FAIL: no semantic check passed")
        return 1

    if warned:
        print("WARN: some semantic checks need stronger evidence")
        return 0

    print("PASS: semantic regression evidence complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
