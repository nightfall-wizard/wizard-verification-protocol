#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/FINDINGS-TRIAGE.json"

REQUIRED_BOUNDARY = [
    "no_real_seed",
    "no_private_key",
    "no_live_funds",
    "no_exploit_payloads",
    "no_public_zero_day_details",
    "non_audit_label_required",
    "sanitized_public_reports",
]

REQUIRED_TEMPLATES = [
    "templates/security/finding-record.json",
    "templates/security/sanitized-finding.md",
    "templates/security/private-disclosure-checklist.md",
]

def main():
    if not REPORT.exists():
        print("FAIL: FINDINGS-TRIAGE.json missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))

    classes = data.get("security_classes", [])
    severities = data.get("severity_levels", [])
    states = data.get("workflow_states", [])
    rules = data.get("triage_rules", [])
    boundary = data.get("safety_boundary", {})

    print("WVP Findings Triage Check")
    print("Classes:", len(classes))
    print("Severities:", len(severities))
    print("States:", len(states))
    print("Rules:", len(rules))

    if len(classes) < 9:
        print("FAIL: expected at least 9 security classes")
        return 1

    if len(severities) < 5:
        print("FAIL: expected at least 5 severities")
        return 1

    if len(states) < 8:
        print("FAIL: expected at least 8 workflow states")
        return 1

    if len(rules) < 8:
        print("FAIL: expected at least 8 triage rules")
        return 1

    for key in REQUIRED_BOUNDARY:
        if boundary.get(key) is not True:
            print("FAIL: missing safety boundary:", key)
            return 1

    for rel in REQUIRED_TEMPLATES:
        if not (ROOT / rel).exists():
            print("FAIL: missing template:", rel)
            return 1

    high = [s for s in severities if s.get("level") in ["HIGH", "CRITICAL"]]
    if not high or not all(s.get("private_default") is True for s in high):
        print("FAIL: HIGH/CRITICAL must default private")
        return 1

    private_classes = [c for c in classes if c.get("private_default") is True]
    if len(private_classes) < 8:
        print("FAIL: expected security-critical classes to default private")
        return 1

    print("PASS: private disclosure and triage workflow complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
