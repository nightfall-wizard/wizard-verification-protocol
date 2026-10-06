
#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/GOVERNANCE-RELEASE.json"

REQUIRED_FILES = [
    "docs/GOVERNANCE.md",
    "docs/VERSIONING-POLICY.md",
    "docs/RELEASE-PROCESS.md",
    "docs/CHANGELOG-POLICY.md",
    "docs/EVIDENCE-REFRESH-CADENCE.md",
    "docs/MAINTAINER-ROLES.md",
    "CHANGELOG.md",
    "templates/governance/release-checklist.md",
    "templates/governance/versioned-release-note.md",
    "templates/governance/evidence-refresh-issue.md",
    "templates/governance/maintainer-decision-record.md",
    "templates/governance/governance-review-comment.md",
    "reports/nightfall/v1.0.5/GOVERNANCE-RELEASE.md",
]

REQUIRED_PHRASES = [
    "not an audit",
    "not proof",
    "no real seed",
    "no private key",
    "no wallet file",
    "no live funds",
    "no exploit payload",
    "weaponized reproduction",
    "branch protection",
    "independent external review",
    "release pack",
    "version",
]

def main():
    print("WVP Governance Release Check")

    if not REPORT.exists():
        print("FAIL: GOVERNANCE-RELEASE.json missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    controls = data.get("controls", [])
    passed = data.get("control_pass", 0)
    boundary = data.get("safety_boundary", {})

    print("Controls:", len(controls))
    print("PASS:", passed)
    print("Local completion:", data.get("local_completion_percent_after_success"))
    print("External remaining:", data.get("remaining_external_completion_percent"))

    if len(controls) < 15:
        print("FAIL: expected at least 15 governance controls")
        return 1

    if passed < len(controls):
        print("FAIL: not all governance controls passed")
        return 1

    if data.get("local_completion_percent_after_success") != 98:
        print("FAIL: local completion percent must be 98")
        return 1

    if data.get("remaining_external_completion_percent") != 2:
        print("FAIL: remaining external completion percent must be 2")
        return 1

    required_boundary = [
        "no_real_seed",
        "no_private_key",
        "no_wallet_file",
        "no_live_funds",
        "no_exploit_payloads",
        "no_weaponized_reproduction",
        "public_report_sanitized",
        "non_audit_boundary_required",
    ]

    for key in required_boundary:
        if boundary.get(key) is not True:
            print("FAIL: missing safety boundary:", key)
            return 1

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            print("FAIL: missing required governance file:", rel)
            return 1

    combined = ""
    for rel in REQUIRED_FILES:
        combined += "\n" + (ROOT / rel).read_text(encoding="utf-8", errors="replace").lower()

    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in combined:
            print("FAIL: missing required phrase:", phrase)
            return 1

    remaining = data.get("remaining_external_actions", [])
    if len(remaining) < 5:
        print("FAIL: remaining external actions not documented")
        return 1

    print("PASS: repository governance and versioned release process complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
