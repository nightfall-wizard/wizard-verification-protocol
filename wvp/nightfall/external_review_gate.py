
#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = ROOT / "reports/nightfall/v1.0.5/EXTERNAL-REVIEW.json"
GATE = ROOT / "reports/nightfall/v1.0.5/ISSUE-QUALITY-GATE.json"

REQUIRED_FILES = [
    "docs/EXTERNAL-REVIEW-PREPARATION.md",
    "docs/ISSUE-QUALITY-GATE-METHOD.md",
    "docs/EXTERNAL-REVIEW-REQUEST.md",
    "docs/REVIEW-SCOPE.md",
    "docs/REVIEWER-RESPONSE-LOG.md",
    "templates/issues/evidence-gap.md",
    "templates/issues/reviewer-question.md",
    "templates/issues/sanitized-security-observation.md",
    "templates/review/external-review-request.md",
    "templates/review/reviewer-response-log.md",
    "templates/review/review-scope-confirmation.md",
    "reports/nightfall/v1.0.5/EXTERNAL-REVIEW.md",
    "reports/nightfall/v1.0.5/ISSUE-QUALITY-GATE.md",
]

REQUIRED_PHRASES = [
    "not an audit",
    "external review",
    "issue-quality gate",
    "private key",
    "seed",
    "live funds",
    "exploit payload",
    "weaponized reproduction",
    "undisclosed vulnerability detail",
    "not proof",
]

def main():
    print("WVP External Review Gate Check")

    if not EXTERNAL.exists():
        print("FAIL: EXTERNAL-REVIEW.json missing")
        return 1

    if not GATE.exists():
        print("FAIL: ISSUE-QUALITY-GATE.json missing")
        return 1

    external = json.loads(EXTERNAL.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))

    items = external.get("items", [])
    item_pass = external.get("review_item_pass", 0)
    rules = gate.get("rules", [])
    rule_pass = gate.get("gate_rule_pass", 0)
    boundary = external.get("safety_boundary", {})

    print("Review items:", len(items))
    print("Review PASS:", item_pass)
    print("Gate rules:", len(rules))
    print("Gate PASS:", rule_pass)

    if len(items) < 12:
        print("FAIL: expected at least 12 external review items")
        return 1

    if item_pass < len(items):
        print("FAIL: not all external review items passed")
        return 1

    if len(rules) < 12:
        print("FAIL: expected at least 12 issue-quality gate rules")
        return 1

    if rule_pass < len(rules):
        print("FAIL: not all issue-quality gate rules passed")
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
            print("FAIL: missing required external-review file:", rel)
            return 1

    combined = ""
    for rel in REQUIRED_FILES:
        combined += "\n" + (ROOT / rel).read_text(encoding="utf-8", errors="replace").lower()

    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in combined:
            print("FAIL: missing required phrase:", phrase)
            return 1

    print("PASS: external review preparation and issue-quality gate complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
