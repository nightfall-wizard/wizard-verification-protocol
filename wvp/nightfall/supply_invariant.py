#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/SUPPLY-INVARIANT-MAP.json"

def main():
    if not REPORT.exists():
        print("FAIL: SUPPLY-INVARIANT-MAP.json missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    claims = data.get("claim_count", 0)
    claim_pass = data.get("claim_pass", 0)
    claim_warn = data.get("claim_warn", 0)
    probes = data.get("probe_count", 0)
    probe_pass = data.get("probe_pass", 0)
    probe_warn = data.get("probe_warn", 0)

    print("WVP Supply Invariant Evidence Check")
    print("Claims:", claims)
    print("Claim PASS:", claim_pass)
    print("Claim WARN:", claim_warn)
    print("Probes:", probes)
    print("Probe PASS:", probe_pass)
    print("Probe WARN:", probe_warn)

    if claims < 8:
        print("FAIL: expected at least 8 invariant claims")
        return 1

    if claim_pass < 6:
        print("FAIL: too little invariant evidence")
        return 1

    if probes < 5:
        print("FAIL: expected at least 5 runtime-safe probes")
        return 1

    if probe_pass < 4:
        print("FAIL: too little runtime-safe probe evidence")
        return 1

    if claim_warn or probe_warn:
        print("WARN: some invariant evidence requires manual review")
        return 0

    print("PASS: supply invariant evidence complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
