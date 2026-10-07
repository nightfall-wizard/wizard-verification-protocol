#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "reports/auneya/reviewer-packet-v0.1"

REQUIRED_FILES = [
    "docs/auneya/AUNEYA-PROTOCOL-CHARTER.md",
    "docs/auneya/AUNEYA-PROVABLE-WEB-SCOPE.md",
    "docs/auneya/AUNEYA-NON-VALUE-SIMULATION-NOTICE.md",
    "docs/auneya/AUNEYA-CLAIM-SCHEMA-V0.1.md",
    "docs/auneya/AUNEYA-WITNESS-PROOF-SCHEMA-V0.1.md",
    "docs/auneya/AUNEYA-EVENT-SCHEMA-V0.1.md",
    "docs/auneya/AUNEYA-PULSE-AND-PROOFLET-FLOW-V0.1.md",
    "docs/auneya/AUNEYA-LOCAL-WITNESS-RUNNER-V0.1.md",
    "docs/auneya/AUNEYA-LOCAL-SIMULATION-EVIDENCE-PACK-V0.1.md",
    "docs/auneya/AUNEYA-EXTERNAL-REVIEW-READINESS-V0.1.md",
    "docs/auneya/AUNEYA-PUBLIC-DOCUMENTATION-QUALITY-GATE-V0.1.md",
    "docs/auneya/AUNEYA-EXTERNAL-REVIEWER-PACKET-V0.1.md",
    "docs/auneya/AUNEYA-REVIEW-FEEDBACK-WORKFLOW-V0.1.md",
    ".github/ISSUE_TEMPLATE/auneya_external_review.yml",
]

REQUIRED_TERMS = [
    "external reviewer packet",
    "feedback workflow",
    "review categories",
    "review questions",
    "issue template",
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

ISSUE_TEMPLATE_TERMS = [
    "AUNEYA external review",
    "Review area",
    "Summary",
    "Evidence or file reference",
    "Boundary confirmation",
    "No token",
    "No market value",
    "No transferability",
    "No mainnet",
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
        checks.append(term_check(term, corpus, "packet_term"))

    issue_text = read(ROOT / ".github/ISSUE_TEMPLATE/auneya_external_review.yml")
    for term in ISSUE_TEMPLATE_TERMS:
        checks.append(term_check(term, issue_text, "issue_template_term"))

    passed = sum(1 for c in checks if c["status"] == "pass")
    failed = [c for c in checks if c["status"] != "pass"]

    evidence = {
        "evidence_pack": "auneya-reviewer-packet-v0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "external_reviewer_packet",
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
        "reviewer_packet": {
            "reviewer_packet_doc": "docs/auneya/AUNEYA-EXTERNAL-REVIEWER-PACKET-V0.1.md",
            "feedback_workflow_doc": "docs/auneya/AUNEYA-REVIEW-FEEDBACK-WORKFLOW-V0.1.md",
            "issue_template": ".github/ISSUE_TEMPLATE/auneya_external_review.yml",
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

    json_path = OUT_DIR / "AUNEYA-REVIEWER-PACKET-v0.1.json"
    md_path = OUT_DIR / "AUNEYA-REVIEWER-PACKET-v0.1.md"

    json_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# AUNEYA Reviewer Packet v0.1",
        "",
        "Status: " + evidence["overall_status"].upper(),
        "",
        "Mode: external reviewer packet",
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
        "## Checks",
        "",
        "| Check | Status |",
        "|---|---:|",
    ]

    for c in checks:
        lines.append(f"| `{c['id']}` | `{c['status']}` |")

    lines += [
        "",
        "## Reviewer packet",
        "",
        "- `docs/auneya/AUNEYA-EXTERNAL-REVIEWER-PACKET-V0.1.md`",
        "- `docs/auneya/AUNEYA-REVIEW-FEEDBACK-WORKFLOW-V0.1.md`",
        "- `.github/ISSUE_TEMPLATE/auneya_external_review.yml`",
        "",
        "## Boundary",
        "",
        "This reviewer packet makes AUNEYA externally reviewable as documentation and local non-value simulation evidence.",
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

