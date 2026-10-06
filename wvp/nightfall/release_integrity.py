#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/RELEASE-INTEGRITY.json"

def main():
    if not REPORT.exists():
        print("FAIL: RELEASE-INTEGRITY.json missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    total = data.get("evidence_count", 0)
    passed = data.get("passed", 0)
    warned = data.get("warned", 0)
    hashes = data.get("hashes", [])

    print("WVP Release Integrity Check")
    print("Evidence:", total)
    print("PASS:", passed)
    print("WARN:", warned)
    print("Hashes:", len(hashes))

    if total < 8:
        print("FAIL: expected at least 8 evidence checks")
        return 1

    if passed < 6:
        print("FAIL: too little release integrity evidence")
        return 1

    existing_hashes = [h for h in hashes if h.get("exists") and h.get("sha256")]
    if len(existing_hashes) < 3:
        print("FAIL: not enough hashed release-relevant files")
        return 1

    if warned:
        print("WARN: some release evidence requires manual review")
        return 0

    print("PASS: release integrity evidence complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
