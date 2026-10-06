
#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/nightfall/v1.0.5/EXTERNAL-COMPLETION.json"

REQUIRED_FILES = [
    "docs/EXTERNAL-COMPLETION-CHECKLIST.md",
    "docs/PR-MERGE-WORKFLOW.md",
    "docs/BRANCH-PROTECTION-VERIFICATION.md",
    "docs/CI-HISTORY-VERIFICATION.md",
    "docs/INDEPENDENT-REVIEW-TRACKER.md",
    "docs/FINAL-COMPLETION-BOUNDARY.md",
    "templates/external/final-completion-record.md",
    "templates/external/pr-merge-record.md",
    "templates/external/branch-protection-record.md",
    "templates/external/ci-run-record.md",
    "templates/external/external-review-record.md",
    "reports/nightfall/v1.0.5/EXTERNAL-COMPLETION.md",
]

REQUIRED_PHRASES = [
    "not an audit",
    "not proof",
    "branch protection",
    "github actions",
    "pull request",
    "external review",
    "100 percent",
    "termux",
    "no real seed",
    "no private key",
    "no live funds",
    "no exploit payload",
]

def main():
    print("WVP External Completion Check")

    if not REPORT.exists():
        print("FAIL: EXTERNAL-COMPLETION.json missing")
        return 1

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    controls = data.get("controls", [])
    passed = data.get("control_pass", 0)
    boundary = data.get("safety_boundary", {})

    print("Controls:", len(controls))
    print("PASS:", passed)
    print("Local completion:", data.get("local_completion_percent_after_success"))
    print("External remaining:", data.get("remaining_external_completion_percent"))
    print("Termux true 100%:", data.get("termux_can_set_true_100_percent"))

    if len(controls) < 14:
        print("FAIL: expected at least 14 external completion controls")
        return 1

    if passed < len(controls):
        print("FAIL: not all external completion controls passed")
        return 1

    if data.get("local_completion_percent_after_success") != 99:
        print("FAIL: local completion percent must be 99")
        return 1

    if data.get("remaining_external_completion_percent") != 1:
        print("FAIL: remaining external completion percent must be 1")
        return 1

    if data.get("termux_can_set_true_100_percent") is not False:
        print("FAIL: Termux true 100 percent boundary must be false")
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
            print("FAIL: missing required external completion file:", rel)
            return 1

    combined = ""
    for rel in REQUIRED_FILES:
        combined += "\n" + (ROOT / rel).read_text(encoding="utf-8", errors="replace").lower()

    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in combined:
            print("FAIL: missing required phrase:", phrase)
            return 1

    if len(data.get("remaining_external_actions", [])) < 6:
        print("FAIL: remaining external actions incomplete")
        return 1

    if len(data.get("conditions_for_true_100_percent", [])) < 6:
        print("FAIL: true 100 percent conditions incomplete")
        return 1

    print("PASS: external completion checklist and verification process complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
