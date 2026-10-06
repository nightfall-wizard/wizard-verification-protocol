#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/COMMAND-PROBES.json"

def main():
    if not REPORT.exists():
        print("FAIL: COMMAND-PROBES.json missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    total = data.get("probe_count", 0)
    passed = data.get("passed", 0)
    warned = data.get("warned", 0)

    print("WVP Command Probe Check")
    print("Probes:", total)
    print("PASS:", passed)
    print("WARN:", warned)

    if total < 8:
        print("FAIL: expected at least 8 probes")
        return 1

    if passed < 5:
        print("FAIL: too little command evidence")
        return 1

    if warned:
        print("WARN: some probes need manual review")
        return 0

    print("PASS: command probe evidence complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
