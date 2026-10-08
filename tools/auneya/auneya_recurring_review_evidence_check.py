#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "reports/auneya/recurring-review-evidence-v0.1"

REQUIRED_FILES = [
    "docs/auneya/AUNEYA-EXTERNAL-REVIEWER-PACKET-V0.1.md",
    "docs/auneya/AUNEYA-REVIEW-FEEDBACK-WORKFLOW-V0.1.md",
    "docs/auneya/AUNEYA-REVIEW-INTAKE-EVIDENCE-V0.1.md",
    "docs/auneya/AUNEYA-MAINTAINER-RESPONSE-LOG-V0.1.md",
    "docs/auneya/AUNEYA-RECURRING-REVIEW-EVIDENCE-REFRESH-V0.1.md",
    "docs/auneya/AUNEYA-EXTERNAL-FEEDBACK-TRAIL-V0.1.md",
    ".github/ISSUE_TEMPLATE/auneya_external_review.yml",
    ".github/ISSUE_TEMPLATE/auneya_maintainer_response.yml",
    ".github/workflows/auneya-recurring-review-evidence.yml",
]

REQUIRED_TERMS = [
    "recurring review evidence refresh",
    "external feedback trail",
    "refresh cadence",
    "weekly scheduled check",
    "workflow_dispatch",
    "schedule",
    "zero-feedback state",
    "do not create fake external feedback",
    "review intake evidence",
    "maintainer response log",
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

REQUIRED_TRAIL_FIELDS = [
    "trail_id",
    "cycle_id",
    "refresh_type",
    "source",
    "issue_count",
    "external_feedback_received",
    "fake_feedback_created",
    "linked_issue",
    "maintainer_status",
    "boundary_impact",
    "legal_review_required",
    "technical_review_required",
    "created_at",
    "updated_at",
]

REQUIRED_WORKFLOW_TERMS = [
    "AUNEYA Recurring Review Evidence",
    "workflow_dispatch",
    "schedule",
    "auneya-recurring-review-evidence-v0.1.sh",
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

    for term in REQUIRED_TERMS:
        checks.append(term_check(term, corpus, "required_term"))

    for field in REQUIRED_TRAIL_FIELDS:
        checks.append(term_check(field, corpus, "trail_field"))

    workflow_text = read(ROOT / ".github/workflows/auneya-recurring-review-evidence.yml")
    for term in REQUIRED_WORKFLOW_TERMS:
        checks.append(term_check(term, workflow_text, "workflow_term"))

    passed = sum(1 for c in checks if c["status"] == "pass")
    failed = [c for c in checks if c["status"] != "pass"]

    evidence = {
        "evidence_pack": "auneya-recurring-review-evidence-v0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "recurring_review_evidence_refresh_and_external_feedback_trail",
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
        "recurring_review_state": {
            "cycle_id": "initial-recurring-review-cycle-v0.1",
            "refresh_type": "initial_zero_feedback_refresh",
            "refresh_cadence": "weekly scheduled check plus manual workflow_dispatch",
            "external_feedback_received": False,
            "fake_feedback_created": False,
            "issue_count": 0,
            "trail_entries": [],
            "reason": "No independent external AUNEYA review issue is recorded in this initial recurring refresh artifact. The trail exists without inventing feedback.",
        },
        "external_feedback_trail_fields": REQUIRED_TRAIL_FIELDS,
        "workflow": {
            "path": ".github/workflows/auneya-recurring-review-evidence.yml",
            "manual_dispatch": True,
            "scheduled_check": True,
            "local_conformance_script": "conformance/auneya-recurring-review-evidence-v0.1.sh",
        },
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

    json_path = OUT_DIR / "AUNEYA-RECURRING-REVIEW-EVIDENCE-v0.1.json"
    md_path = OUT_DIR / "AUNEYA-RECURRING-REVIEW-EVIDENCE-v0.1.md"

    json_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# AUNEYA Recurring Review Evidence v0.1",
        "",
        "Status: " + evidence["overall_status"].upper(),
        "",
        "Mode: recurring review evidence refresh and external feedback trail",
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
        "## Recurring review state",
        "",
        "- Cycle ID: `initial-recurring-review-cycle-v0.1`",
        "- Refresh type: `initial_zero_feedback_refresh`",
        "- Refresh cadence: weekly scheduled check plus manual workflow_dispatch",
        "- External feedback received: false",
        "- Fake feedback created: false",
        "- Issue count: 0",
        "",
        "No independent external AUNEYA review issue is recorded in this initial recurring refresh artifact. The trail exists without inventing feedback.",
        "",
        "## External feedback trail fields",
        "",
    ]

    for field in REQUIRED_TRAIL_FIELDS:
        lines.append(f"- `{field}`")

    lines += [
        "",
        "## Workflow",
        "",
        "- `.github/workflows/auneya-recurring-review-evidence.yml`",
        "- manual `workflow_dispatch` supported",
        "- weekly scheduled check supported",
        "- local conformance script: `conformance/auneya-recurring-review-evidence-v0.1.sh`",
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
        "This artifact creates a recurring evidence refresh and external feedback trail for AUNEYA non-value simulation documentation.",
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

