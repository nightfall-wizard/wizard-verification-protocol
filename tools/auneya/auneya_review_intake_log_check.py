#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "reports/auneya/review-intake-log-v0.1"

REQUIRED_FILES = [
    "docs/auneya/AUNEYA-EXTERNAL-REVIEWER-PACKET-V0.1.md",
    "docs/auneya/AUNEYA-REVIEW-FEEDBACK-WORKFLOW-V0.1.md",
    "docs/auneya/AUNEYA-REVIEW-INTAKE-EVIDENCE-V0.1.md",
    "docs/auneya/AUNEYA-MAINTAINER-RESPONSE-LOG-V0.1.md",
    ".github/ISSUE_TEMPLATE/auneya_external_review.yml",
    ".github/ISSUE_TEMPLATE/auneya_maintainer_response.yml",
]

REQUIRED_FIELDS = [
    "review_id",
    "source",
    "review_area",
    "summary",
    "risk_level",
    "maintainer_status",
    "maintainer_response",
    "boundary_impact",
    "legal_review_required",
    "technical_review_required",
    "accepted_change_required",
    "linked_issue",
    "created_at",
    "updated_at",
]

REQUIRED_TERMS = [
    "review intake evidence",
    "maintainer response log",
    "zero-intake state",
    "do not create fake reviewer feedback",
    "review categories",
    "triage states",
    "boundary impact",
    "non-value simulation",
    "no token",
    "no market value",
    "no transferability",
    "no mainnet",
    "not investment advice",
    "not legal advice",
    "not a custody, broker, exchange or financial service",
    "legal review",
]

REQUIRED_STATUSES = [
    "accepted",
    "needs clarification",
    "needs legal review",
    "needs technical review",
    "deferred",
    "rejected",
    "duplicate",
    "out of scope",
]

ISSUE_TEMPLATE_TERMS = [
    "AUNEYA maintainer response",
    "Maintainer status",
    "Boundary impact",
    "Legal review required",
    "Technical review required",
    "Accepted change required",
    "Linked issue",
]

def read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")

def file_check(rel: str) -> dict:
    p = ROOT / rel
    return {
        "id": "file_exists:" + rel,
        "status": "pass" if p.exists() and p.is_file() else "fail",
        "path": rel,
    }

def term_check(term: str, corpus: str, group: str) -> dict:
    return {
        "id": group + ":" + term,
        "status": "pass" if term.lower() in corpus.lower() else "fail",
        "term": term,
    }

def main() -> int:
    checks = []

    for rel in REQUIRED_FILES:
        checks.append(file_check(rel))

    corpus = "\n".join(read(ROOT / rel) for rel in REQUIRED_FILES)

    for field in REQUIRED_FIELDS:
        checks.append(term_check(field, corpus, "required_field"))

    for term in REQUIRED_TERMS:
        checks.append(term_check(term, corpus, "required_term"))

    for status in REQUIRED_STATUSES:
        checks.append(term_check(status, corpus, "triage_status"))

    issue_text = read(ROOT / ".github/ISSUE_TEMPLATE/auneya_maintainer_response.yml")
    for term in ISSUE_TEMPLATE_TERMS:
        checks.append(term_check(term, issue_text, "maintainer_template_term"))

    passed = sum(1 for c in checks if c["status"] == "pass")
    failed = [c for c in checks if c["status"] != "pass"]

    evidence = {
        "evidence_pack": "auneya-review-intake-log-v0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "review_intake_evidence_and_maintainer_response_log",
        "network": "none",
        "mainnet_active": False,
        "token_created": False,
        "market_value_claimed": False,
        "transferable": False,
        "overall_status": "pass" if not failed else "fail",
        "score": {
            "passed": passed,
            "total": len(checks),
            "percent": round((passed / len(checks)) * 100, 2) if checks else 0,
        },
        "checks": checks,
        "failed": failed,
        "review_intake_state": {
            "zero_intake_state": True,
            "external_review_received": False,
            "fake_reviewer_feedback_created": False,
            "intake_entries": [],
            "reason": "No independent external reviewer issue has been received in this artifact. The log records schema readiness without inventing external feedback.",
        },
        "required_fields": REQUIRED_FIELDS,
        "allowed_maintainer_statuses": REQUIRED_STATUSES,
        "boundary": {
            "no_token": True,
            "no_market_value": True,
            "no_transferability": True,
            "no_mainnet": True,
            "not_investment_advice": True,
            "not_legal_advice": True,
            "not_financial_service": True,
            "legal_review_required_before_launch": True,
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = OUT_DIR / "AUNEYA-REVIEW-INTAKE-LOG-v0.1.json"
    md_path = OUT_DIR / "AUNEYA-REVIEW-INTAKE-LOG-v0.1.md"

    json_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# AUNEYA Review Intake Log v0.1",
        "",
        "Status: " + evidence["overall_status"].upper(),
        "",
        "Mode: review intake evidence and maintainer response log",
        "Network: none",
        "Mainnet active: false",
        "Token created: false",
        "Market value claimed: false",
        "Transferable: false",
        "",
        "## Score",
        "",
        f"{passed}/{len(checks)} checks passed.",
        "",
        "## Intake state",
        "",
        "- Zero-intake state: true",
        "- External review received: false",
        "- Fake reviewer feedback created: false",
        "",
        "No independent external reviewer issue has been received in this artifact. This report records schema readiness without inventing external feedback.",
        "",
        "## Required fields",
        "",
    ]

    for field in REQUIRED_FIELDS:
        lines.append(f"- `{field}`")

    lines += [
        "",
        "## Maintainer statuses",
        "",
    ]

    for status in REQUIRED_STATUSES:
        lines.append(f"- `{status}`")

    lines += [
        "",
        "## Checks",
        "",
        "| Check | Status |",
        "|---|---:|",
    ]

    for c in checks:
        lines.append(f"| `{c['id']}` | `{c['status']}` |")

    lines += [
        "",
        "## Boundary",
        "",
        "This artifact creates a review intake and maintainer response structure for AUNEYA non-value simulation documentation.",
        "",
        "It does not create AUNEYA, neya, a token, market value, transferability, mainnet activity, legal clearance, financial claims or financial-service activity.",
        "",
        "Legal review is required before any public token launch, listing, sale, transferability or market-value communication.",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("Evidence JSON:", json_path)
    print("Evidence MD:  ", md_path)
    print("Status:       ", evidence["overall_status"].upper())
    print("Score:        ", f"{passed}/{len(checks)}")

    return 0 if not failed else 1

if __name__ == "__main__":
    raise SystemExit(main())

