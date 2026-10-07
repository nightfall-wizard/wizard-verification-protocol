#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "reports/auneya/external-review-readiness-v0.1"

REQUIRED_DOCS = [
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
]

REQUIRED_BOUNDARY_TERMS = [
    "no token",
    "no market value",
    "no transferability",
    "no mainnet",
    "not investment advice",
    "not legal advice",
    "not a custody",
    "legal review",
    "non-value",
]

REVIEW_READINESS_TERMS = [
    "review scope",
    "reviewer checklist",
    "public documentation",
    "open questions",
    "known limitations",
    "non-value simulation",
    "external review",
    "quality gate",
]

def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")

def check_doc_exists(rel: str) -> dict:
    p = ROOT / rel
    return {
        "id": "doc_exists:" + rel,
        "status": "pass" if p.exists() and p.is_file() else "fail",
        "path": rel,
    }

def check_term(term: str, corpus: str, group: str) -> dict:
    ok = term.lower() in corpus.lower()
    return {
        "id": group + ":" + term,
        "status": "pass" if ok else "fail",
        "term": term,
    }

def main() -> int:
    checks = []

    for rel in REQUIRED_DOCS:
        checks.append(check_doc_exists(rel))

    corpus_parts = []
    for rel in REQUIRED_DOCS:
        corpus_parts.append(read_text(ROOT / rel))
    corpus = "\n".join(corpus_parts)

    for term in REQUIRED_BOUNDARY_TERMS:
        checks.append(check_term(term, corpus, "boundary_term"))

    readiness_docs = "\n".join([
        read_text(ROOT / "docs/auneya/AUNEYA-EXTERNAL-REVIEW-READINESS-V0.1.md"),
        read_text(ROOT / "docs/auneya/AUNEYA-PUBLIC-DOCUMENTATION-QUALITY-GATE-V0.1.md"),
    ])

    for term in REVIEW_READINESS_TERMS:
        checks.append(check_term(term, readiness_docs, "readiness_term"))

    passed = sum(1 for c in checks if c["status"] == "pass")
    failed = [c for c in checks if c["status"] != "pass"]

    evidence = {
        "evidence_pack": "auneya-external-review-readiness-v0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "documentation_quality_gate",
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

    json_path = OUT_DIR / "AUNEYA-EXTERNAL-REVIEW-READINESS-v0.1.json"
    md_path = OUT_DIR / "AUNEYA-EXTERNAL-REVIEW-READINESS-v0.1.md"

    json_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# AUNEYA External Review Readiness v0.1",
        "",
        "Status: " + evidence["overall_status"].upper(),
        "",
        "Mode: documentation quality gate",
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
        "## Required checks",
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
        "This report checks whether AUNEYA is externally reviewable as documentation and local non-value simulation evidence.",
        "",
        "It does not create AUNEYA, neya, a token, market value, transferability, mainnet activity, investment claims, legal clearance or financial-service activity.",
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

